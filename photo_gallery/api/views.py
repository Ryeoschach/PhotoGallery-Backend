from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, ImageSerializer, GroupSerializer, HomeLayoutSerializer, CaptchaSerializer, CaptchaValidationSerializer, LoginWithCaptchaSerializer
from .models import Image, Group, HomeLayout, Captcha
from .utils import generate_captcha_code, create_captcha_image, cleanup_expired_captchas
import uuid

# 自定义权限类，用于确保用户只能修改/删除自己上传的图片
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 读取请求总是允许的
        if request.method in permissions.SAFE_METHODS:
            return True
        # 写权限只允许图片的上传者
        return obj.owner == request.user

# 用户注册视图
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# 当前用户视图
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [permissions.IsAdminUser]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed, created, updated, and deleted.
    """
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        # 默认显示全部图片
        queryset = Image.objects.all().order_by('-uploaded_at')
        
        # 如果请求中包含 ?mine=true 参数，则只返回当前用户的图片
        mine = self.request.query_params.get('mine', None)
        if mine and mine.lower() == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(owner=self.request.user)
        
        return queryset

    def create(self, request, *args, **kwargs):
        print("--- Debugging Image Upload ---")
        print(f"Request Method: {request.method}")
        print(f"Request Headers: {request.headers}")
        print(f"Request Content-Type: {request.content_type}")
        print(f"Request Data (request.data): {request.data}")
        print(f"Request Files (request.FILES): {request.FILES}")
        print("--- End Debugging ---")
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # 自动设置上传图片的用户为当前登录用户
        serializer.save(owner=self.request.user)

class HomeLayoutViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing home page layouts.
    """
    serializer_class = HomeLayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # 只允许用户访问自己的布局
        queryset = HomeLayout.objects.filter(user=self.request.user).order_by('-updated_at')
        
        # 支持通过名称搜索布局
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
            
        return queryset
    
    def perform_create(self, serializer):
        # 创建时自动关联当前用户
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取用户当前激活的布局"""
        try:
            layout = HomeLayout.objects.get(user=request.user, is_active=True)
            serializer = self.get_serializer(layout)
            return Response(serializer.data)
        except HomeLayout.DoesNotExist:
            # 如果没有激活的布局，尝试创建一个默认布局
            try:
                # 创建默认布局
                default_layout = HomeLayout.objects.create(
                    user=request.user,
                    name="默认网格布局",
                    is_active=True,
                    config={
                        "layout_type": "grid",
                        "xs": 1, "sm": 2, "md": 3, "lg": 4, "xl": 4, "xxl": 6,
                        "image_spacing": 12, "grid_padding": 20
                    }
                )
                serializer = self.get_serializer(default_layout)
                return Response(serializer.data)
            except Exception as e:
                # 如果创建默认布局也失败，则返回错误
                return Response(
                    {"config": {}, "message": f"No active layout found and failed to create default: {str(e)}"},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """将指定布局设为活跃布局"""
        layout = self.get_object()
        layout.is_active = True
        layout.save()
        serializer = self.get_serializer(layout)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def update_spacing(self, request, pk=None):
        """更新布局的图片间隔设置"""
        layout = self.get_object()
        config = layout.config
        
        # 获取请求中的值，如果没有提供则使用当前值
        image_spacing = request.data.get('image_spacing', config.get('image_spacing', 8))
        grid_padding = request.data.get('grid_padding', config.get('grid_padding', 16))
        
        # 更新配置
        config['image_spacing'] = int(image_spacing)
        config['grid_padding'] = int(grid_padding)
        layout.config = config
        layout.save()
        
        serializer = self.get_serializer(layout)
        return Response(serializer.data)

class CaptchaView(APIView):
    """验证码生成视图"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """生成新的验证码"""
        # 清理过期的验证码
        cleanup_expired_captchas()
        
        # 生成验证码
        code = generate_captcha_code()
        session_key = str(uuid.uuid4())
        
        # 创建验证码图片
        image_file = create_captcha_image(code)
        
        # 保存到数据库
        captcha = Captcha.objects.create(
            session_key=session_key,
            code=code,
            image=image_file
        )
        
        # 序列化并返回
        serializer = CaptchaSerializer(captcha, context={'request': request})
        return Response(serializer.data)


class CaptchaValidationView(APIView):
    """验证码验证视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """验证验证码"""
        serializer = CaptchaValidationSerializer(data=request.data)
        if serializer.is_valid():
            # 验证码正确，标记为已使用
            captcha = serializer.validated_data['captcha']
            captcha.mark_as_used()
            
            return Response({
                'success': True,
                'message': '验证码验证成功'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginWithCaptchaView(APIView):
    """带验证码的登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """使用用户名密码和验证码登录"""
        serializer = LoginWithCaptchaSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            captcha = serializer.validated_data['captcha']
            
            # 验证用户名和密码
            user = authenticate(username=username, password=password)
            if user is None:
                return Response({
                    'success': False,
                    'message': '用户名或密码错误'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'success': False,
                    'message': '用户账户已被禁用'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 标记验证码为已使用
            captcha.mark_as_used()
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': '登录成功',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
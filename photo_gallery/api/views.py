from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer, ImageSerializer, GroupSerializer, HomeLayoutSerializer
from .models import Image, Group, HomeLayout

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
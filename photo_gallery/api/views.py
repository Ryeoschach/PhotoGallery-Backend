from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer, ImageSerializer, GroupSerializer
from .models import Image, Group

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
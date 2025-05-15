from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .serializers import UserSerializer, ImageSerializer, GroupSerializer
from .models import Image, Group

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
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly] # 根据需要设置权限

class ImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows images to be viewed, created, updated, and deleted.
    """
    queryset = Image.objects.all().order_by('-uploaded_at')
    serializer_class = ImageSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        print("--- Debugging Image Upload ---")
        print(f"Request Method: {request.method}")
        print(f"Request Headers: {request.headers}")
        print(f"Request Content-Type: {request.content_type}")
        print(f"Request Data (request.data): {request.data}") # 应该会包含 "groups": [id1, id2]
        print(f"Request Files (request.FILES): {request.FILES}")
        print("--- End Debugging ---")
        
        return super().create(request, *args, **kwargs)

    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)
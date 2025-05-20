from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

# 创建一个路由器并注册我们的视图集
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'images', views.ImageViewSet, basename='image')
router.register(r'groups', views.GroupViewSet, basename='group')

# API URL 由路由器自动确定
urlpatterns = [
    path('', include(router.urls)),
    # 新增用户注册端点
    path('register/', views.RegisterView.as_view(), name='register'),
    # 新增获取当前用户信息端点
    path('me/', views.CurrentUserView.as_view(), name='me'),
    # JWT 认证端点
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
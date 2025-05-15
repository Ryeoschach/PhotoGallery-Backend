from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建一个路由器并注册我们的视图集
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'images', views.ImageViewSet, basename='image')
router.register(r'groups', views.GroupViewSet, basename='group') # 新增这一行

# API URL 由路由器自动确定。
urlpatterns = [
    path('', include(router.urls)),
]
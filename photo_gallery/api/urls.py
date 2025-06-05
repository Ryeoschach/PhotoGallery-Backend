from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from django.db import migrations
import json

# 创建一个路由器并注册我们的视图集
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'images', views.ImageViewSet, basename='image')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'layouts', views.HomeLayoutViewSet, basename='layout')  # 新增布局路由

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
    # 验证码相关端点
    path('captcha/', views.CaptchaView.as_view(), name='captcha'),
    path('captcha/validate/', views.CaptchaValidationView.as_view(), name='captcha_validate'),
    path('login-with-captcha/', views.LoginWithCaptchaView.as_view(), name='login_with_captcha'),
]

DEFAULT_LAYOUT = {
    "columns": 3,
    "featured_images": [1, 2, 3],
    "featured_groups": [1],
    "show_recent": True,
    "recent_count": 6,
    "image_spacing": 8,  # 图片间隔，单位为像素
    "grid_padding": 16   # 整个网格的内边距
}

def create_default_layouts(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    HomeLayout = apps.get_model('api', 'HomeLayout')
    
    # 为每个现有用户创建默认布局
    for user in User.objects.all():
        HomeLayout.objects.create(
            user=user,
            name="默认布局",
            is_active=True,
            config=DEFAULT_LAYOUT
        )

def remove_default_layouts(apps, schema_editor):
    HomeLayout = apps.get_model('api', 'HomeLayout')
    HomeLayout.objects.filter(name="默认布局").delete()

def add_spacing_to_layouts(apps, schema_editor):
    HomeLayout = apps.get_model('api', 'HomeLayout')
    
    # 更新所有现有布局配置
    for layout in HomeLayout.objects.all():
        config = layout.config
        if 'image_spacing' not in config:
            config['image_spacing'] = 8  # 默认间隔 8px
        if 'grid_padding' not in config:
            config['grid_padding'] = 16  # 默认内边距 16px
        layout.config = config
        layout.save()

def remove_spacing_from_layouts(apps, schema_editor):
    HomeLayout = apps.get_model('api', 'HomeLayout')
    
    for layout in HomeLayout.objects.all():
        config = layout.config
        if 'image_spacing' in config:
            del config['image_spacing']
        if 'grid_padding' in config:
            del config['grid_padding']
        layout.config = config
        layout.save()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_add_default_layouts'),
    ]

    operations = [
        migrations.RunPython(create_default_layouts, remove_default_layouts),
    ]

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0005_homelayout'),  # 依赖于创建HomeLayout模型的迁移
    ]
    

    operations = [
        migrations.RunPython(add_spacing_to_layouts, remove_spacing_from_layouts),
    ]
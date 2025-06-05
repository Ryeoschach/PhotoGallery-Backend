from django.contrib import admin
from .models import Image, Group, HomeLayout, Captcha

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'uploaded_at', 'width', 'height', 'size')
    list_filter = ('uploaded_at', 'groups')
    search_fields = ('name', 'description', 'owner__username')
    readonly_fields = ('width', 'height', 'size', 'uploaded_at', 'updated_at')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')

@admin.register(HomeLayout)
class HomeLayoutAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Captcha)
class CaptchaAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'code', 'created_at', 'expires_at', 'is_used', 'is_expired')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('session_key', 'code')
    readonly_fields = ('created_at', 'is_expired')
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = '是否过期'

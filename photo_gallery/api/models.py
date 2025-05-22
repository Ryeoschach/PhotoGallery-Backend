from django.db import models
from django.contrib.auth.models import User
import os

def get_upload_path(instance, filename):
    """自定义上传路径，例如：MEDIA_ROOT/user_<id>/<filename>"""
    # 如果你想按用户存储，可以取消注释下一行并确保模型有关联的用户字段
    # return os.path.join(f"user_{instance.owner.id}", filename)
    return filename # 简单起见，直接存储在 MEDIA_ROOT 下

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="分组名称")
    description = models.TextField(blank=True, help_text="分组描述")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Image(models.Model):
    name = models.CharField(max_length=255, blank=True, help_text="图片名称")
    description = models.TextField(blank=True, help_text="图片简介")
    image = models.ImageField(upload_to=get_upload_path, help_text="图片文件")
    width = models.IntegerField(editable=False, null=True, blank=True, help_text="图片宽度 (px)")
    height = models.IntegerField(editable=False, null=True, blank=True, help_text="图片高度 (px)")
    size = models.BigIntegerField(editable=False, null=True, blank=True, help_text="图片大小 (bytes)")
    owner = models.ForeignKey(User, related_name='images', on_delete=models.CASCADE, null=True, blank=True) # 可选：关联上传用户
    groups = models.ManyToManyField(Group, related_name='images', blank=True, help_text="图片所属分组")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"Image {self.id}"

    def save(self, *args, **kwargs):
        if not self.name and self.image:
            self.name = self.image.name

        # 获取并保存图片尺寸和大小
        if self.image:
            try:
                self.width = self.image.width
                self.height = self.image.height
                self.size = self.image.size
            except FileNotFoundError:
                # 处理图片文件可能尚不存在或已被清除的情况
                self.width = None
                self.height = None
                self.size = None
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # 删除模型实例时，同时删除关联的图片文件
        self.image.delete(save=False) # save=False 避免再次调用 save 方法
        super().delete(*args, **kwargs)

class HomeLayout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='layouts')
    name = models.CharField(max_length=100, help_text="布局名称")
    is_active = models.BooleanField(default=False, help_text="是否为当前激活的布局")
    # 存储布局配置为JSON，包含图片间隔和网格内边距等设置
    config = models.JSONField(default=dict, help_text="布局配置JSON，包含image_spacing和grid_padding等设置")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['user', 'is_active']]  # 确保每个用户只有一个激活的布局

    def save(self, *args, **kwargs):
        # 如果当前布局被设置为活跃，则将该用户的其他布局设为非活跃
        if self.is_active:
            HomeLayout.objects.filter(user=self.user, is_active=True).exclude(id=self.id).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

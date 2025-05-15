from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Image, Group # 新增导入 Group

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ('created_at',)

class ImageSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False # 允许在创建/更新时不提供分组
    )
    # 如果你想在 Image 序列化中嵌套完整的 Group 对象而不是仅 ID，可以使用：
    # groups = GroupSerializer(many=True, read_only=True) # 用于只读嵌套
    # 或者对于可写嵌套，你需要更复杂的设置或使用如 drf-writable-nested 库

    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'description',
            'image', # ImageField 会处理文件上传和 URL 生成
            'width',
            'height',
            'size',
            'groups', # 添加 groups 字段
            # 'owner', # 如果你有关联 owner 字段
            # 'owner_username', # 如果你有关联 owner 字段并想显示用户名
            'uploaded_at',
            'updated_at',
        ]
        read_only_fields = ('width', 'height', 'size', 'uploaded_at', 'updated_at') # 这些字段由模型自动填充

    def validate_image(self, value):
        # 可选：添加对图片大小或类型的验证
        # 例如：限制文件大小
        # max_size = 5 * 1024 * 1024 # 5MB
        # if value.size > max_size:
        #     raise serializers.ValidationError(f"图片大小不能超过 {max_size // (1024*1024)}MB.")
        # 例如：限制文件类型
        # allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        # if value.content_type not in allowed_types:
        #     raise serializers.ValidationError(f"不支持的图片类型: {value.content_type}. 支持的类型: {', '.join(allowed_types)}")
        return value
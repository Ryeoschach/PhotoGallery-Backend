from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Image, Group, HomeLayout # 新增导入 HomeLayout

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="确认密码")
    images = serializers.PrimaryKeyRelatedField(many=True, read_only=True) # 用户上传的图片
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password2', 'images', 'is_staff']
        read_only_fields = ('is_staff', 'id')

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password2'):
            raise serializers.ValidationError({"password": "两次输入的密码不匹配。"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ('created_at',)

class ImageSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = Image
        fields = [
            'id',
            'name',
            'description',
            'image',
            'width',
            'height',
            'size',
            'groups',
            'owner',
            'owner_username',
            'uploaded_at',
            'updated_at',
        ]
        read_only_fields = ('width', 'height', 'size', 'uploaded_at', 'updated_at', 'owner', 'owner_username')

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

class HomeLayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeLayout
        fields = ['id', 'name', 'is_active', 'config', 'created_at', 'updated_at']
        read_only_fields = ('created_at', 'updated_at')
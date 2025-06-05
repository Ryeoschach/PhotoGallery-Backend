from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Image, Group, HomeLayout, Captcha # 新增导入 Captcha

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

class CaptchaSerializer(serializers.ModelSerializer):
    """验证码序列化器"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Captcha
        fields = ['session_key', 'image_url', 'created_at', 'expires_at']
        read_only_fields = ('session_key', 'image_url', 'created_at', 'expires_at')
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class CaptchaValidationSerializer(serializers.Serializer):
    """验证码验证序列化器"""
    session_key = serializers.CharField(max_length=128)
    code = serializers.CharField(max_length=10)
    
    def validate(self, attrs):
        session_key = attrs.get('session_key')
        code = attrs.get('code')
        
        try:
            captcha = Captcha.objects.get(session_key=session_key)
        except Captcha.DoesNotExist:
            raise serializers.ValidationError("无效的验证码会话")
        
        if not captcha.is_valid(code):
            if captcha.is_expired():
                raise serializers.ValidationError("验证码已过期")
            elif captcha.is_used:
                raise serializers.ValidationError("验证码已使用")
            else:
                raise serializers.ValidationError("验证码错误")
        
        attrs['captcha'] = captcha
        return attrs


class LoginWithCaptchaSerializer(serializers.Serializer):
    """带验证码的登录序列化器"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    captcha_session_key = serializers.CharField(max_length=128)
    captcha_code = serializers.CharField(max_length=10)
    
    def validate(self, attrs):
        # 首先验证验证码
        captcha_data = {
            'session_key': attrs.get('captcha_session_key'),
            'code': attrs.get('captcha_code')
        }
        captcha_serializer = CaptchaValidationSerializer(data=captcha_data)
        if not captcha_serializer.is_valid():
            raise serializers.ValidationError({"captcha": captcha_serializer.errors})
        
        # 验证码通过后，保存captcha对象供后续使用
        attrs['captcha'] = captcha_serializer.validated_data['captcha']
        
        return attrs
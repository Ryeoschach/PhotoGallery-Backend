"""
验证码生成工具
"""
import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from django.conf import settings


def generate_captcha_code(length=4):
    """生成随机验证码字符串"""
    # 使用数字和大写字母，排除容易混淆的字符
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    return ''.join(random.choice(chars) for _ in range(length))


def create_captcha_image(code, width=120, height=50):
    """
    创建验证码图片
    
    Args:
        code: 验证码文本
        width: 图片宽度
        height: 图片高度
    
    Returns:
        InMemoryUploadedFile: 可以保存到Django ImageField的文件对象
    """
    # 创建图片
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # 尝试加载字体，如果失败则使用默认字体
    try:
        # 你可以根据需要调整字体路径
        font_size = 30
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # 添加背景噪点
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.point((x, y), fill=(random.randint(64, 192), random.randint(64, 192), random.randint(64, 192)))
    
    # 绘制验证码文本
    text_width = draw.textlength(code, font=font)
    x = (width - text_width) // 2
    y = (height - 30) // 2
    
    # 添加文字阴影效果
    draw.text((x + 1, y + 1), code, fill='gray', font=font)
    draw.text((x, y), code, fill='black', font=font)
    
    # 添加干扰线
    for _ in range(3):
        start_x = random.randint(0, width // 2)
        start_y = random.randint(0, height)
        end_x = random.randint(width // 2, width)
        end_y = random.randint(0, height)
        draw.line([(start_x, start_y), (end_x, end_y)], 
                 fill=(random.randint(64, 192), random.randint(64, 192), random.randint(64, 192)), 
                 width=1)
    
    # 保存到内存
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # 创建Django可以处理的文件对象
    file_name = f'captcha_{code}.png'
    django_file = InMemoryUploadedFile(
        buffer, None, file_name, 'image/png', buffer.getvalue().__len__(), None
    )
    
    return django_file


def cleanup_expired_captchas():
    """清理过期的验证码"""
    from .models import Captcha
    from django.utils import timezone
    
    expired_captchas = Captcha.objects.filter(expires_at__lt=timezone.now())
    
    # 删除图片文件
    for captcha in expired_captchas:
        if captcha.image:
            captcha.image.delete(save=False)
    
    # 删除数据库记录
    count = expired_captchas.count()
    expired_captchas.delete()
    
    return count

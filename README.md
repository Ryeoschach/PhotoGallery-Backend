# PhotoGallery-Backend
# 照片库后端 API 文档

这是一个使用 Django REST Framework 构建的照片库后端，支持用户管理、图片上传与管理、照片分组以及首页布局自定义。

## 安装与运行

### 环境要求
- Python 3.8+
- MySQL 数据库

### 安装步骤

1. 克隆仓库
```bash
git clone <repository-url>
cd react-django-photo-gallery/backend
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库
```bash
cd photo_gallery
python manage.py migrate
```

5. 创建管理员账户
```bash
python manage.py createsuperuser
```

6. 运行开发服务器
```bash
python manage.py runserver
```

## API 接口说明

### 1. 用户管理 API

#### 1.1 用户注册
- **URL**: `/api/register/`
- **方法**: `POST`
- **权限**: 允许所有用户 (AllowAny)
- **请求体示例**:
```json
{
  "username": "newuser",
  "password": "securepassword",
  "password2": "securepassword",
  "email": "user@example.com",
  "first_name": "New",
  "last_name": "User"
}
```
- **成功响应**: `201 Created` 用户创建成功

#### 1.2 获取认证令牌
- **URL**: `/api/token/`
- **方法**: `POST`
- **权限**: 允许所有用户 (AllowAny)
- **请求体示例**:
```json
{
  "username": "existinguser",
  "password": "yourpassword"
}
```
- **成功响应**: `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

#### 1.3 刷新认证令牌
- **URL**: `/api/token/refresh/`
- **方法**: `POST`
- **权限**: 允许所有用户 (AllowAny)
- **请求体示例**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```
- **成功响应**: `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

#### 1.4 获取当前用户信息
- **URL**: `/api/me/`
- **方法**: `GET`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `200 OK`
```json
{
  "id": 1,
  "username": "existinguser",
  "email": "user@example.com",
  "first_name": "First",
  "last_name": "Last",
  "images": [1, 2, 3],
  "is_staff": false
}
```

#### 1.5 获取用户列表
- **URL**: `/api/users/`
- **方法**: `GET`
- **权限**: 仅限管理员用户 (IsAdminUser)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `200 OK`
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_staff": true
  }
]
```

#### 1.6 获取特定用户详情
- **URL**: `/api/users/{username}/`
- **方法**: `GET`
- **权限**: 仅限管理员用户 (IsAdminUser)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `200 OK`
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "Admin",
  "last_name": "User",
  "is_staff": true
}
```

### 2. 图片管理 API

#### 2.1 获取图片列表
- **URL**: `/api/images/`
- **方法**: `GET`
- **权限**: 允许任何用户读取 (IsAuthenticatedOrReadOnly)
- **查询参数**: 
  - `mine=true` (可选，仅返回当前用户的图片)
- **成功响应**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "示例图片",
    "description": "这是一张示例图片的描述",
    "image": "http://127.0.0.1:8000/media/example.jpg",
    "width": 1920,
    "height": 1080,
    "size": 1024000,
    "groups": [1, 2],
    "owner": 1,
    "owner_username": "admin",
    "uploaded_at": "2025-05-14T10:30:00Z",
    "updated_at": "2025-05-14T10:30:00Z"
  }
]
```

#### 2.2 获取特定图片详情
- **URL**: `/api/images/{id}/`
- **方法**: `GET`
- **权限**: 允许任何用户读取 (IsAuthenticatedOrReadOnly)
- **成功响应**: `200 OK`
```json
{
  "id": 1,
  "name": "示例图片",
  "description": "这是一张示例图片的描述",
  "image": "http://127.0.0.1:8000/media/example.jpg",
  "width": 1920,
  "height": 1080,
  "size": 1024000,
  "groups": [1, 2],
  "owner": 1,
  "owner_username": "admin",
  "uploaded_at": "2025-05-14T10:30:00Z",
  "updated_at": "2025-05-14T10:30:00Z"
}
```

#### 2.3 上传新图片
- **URL**: `/api/images/`
- **方法**: `POST`
- **权限**: 仅限已认证用户 (IsAuthenticatedOrReadOnly)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: multipart/form-data
```
- **请求体示例** (form-data 格式):
  - `image`: (图片文件)
  - `name`: "我的图片名称"
  - `description`: "图片的详细描述"
  - `groups`: 1 (可选，可多次添加此字段设置多个组)
  - `groups`: 2
- **成功响应**: `201 Created`
```json
{
  "id": 2,
  "name": "我的图片名称",
  "description": "图片的详细描述",
  "image": "http://127.0.0.1:8000/media/myphoto.jpg",
  "width": 800,
  "height": 600,
  "size": 512000,
  "groups": [1, 2],
  "owner": 1,
  "owner_username": "admin",
  "uploaded_at": "2025-05-14T11:30:00Z",
  "updated_at": "2025-05-14T11:30:00Z"
}
```

#### 2.4 更新图片信息
- **URL**: `/api/images/{id}/`
- **方法**: `PUT` 或 `PATCH`
- **权限**: 仅限图片所有者 (IsOwnerOrReadOnly)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: multipart/form-data
```
- **请求体示例** (form-data 格式，PATCH 方法可只包含部分字段):
  - `name`: "更新后的名称"
  - `description`: "更新后的描述"
  - `groups`: 3 
- **成功响应**: `200 OK`

#### 2.5 删除图片
- **URL**: `/api/images/{id}/`
- **方法**: `DELETE`
- **权限**: 仅限图片所有者 (IsOwnerOrReadOnly)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `204 No Content`

### 3. 分组管理 API

#### 3.1 获取分组列表
- **URL**: `/api/groups/`
- **方法**: `GET`
- **权限**: 允许任何用户访问 (默认 AllowAny)
- **成功响应**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "风景",
    "description": "风景照片分组",
    "created_at": "2025-05-14T10:30:00Z"
  }
]
```

#### 3.2 获取特定分组详情
- **URL**: `/api/groups/{id}/`
- **方法**: `GET`
- **权限**: 允许任何用户访问 (默认 AllowAny)
- **成功响应**: `200 OK`
```json
{
  "id": 1,
  "name": "风景",
  "description": "风景照片分组",
  "created_at": "2025-05-14T10:30:00Z"
}
```

#### 3.3 创建新分组
- **URL**: `/api/groups/`
- **方法**: `POST`
- **权限**: 允许任何用户访问 (默认 AllowAny)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: application/json
```
- **请求体示例**:
```json
{
  "name": "人物",
  "description": "人物照片分组"
}
```
- **成功响应**: `201 Created`

#### 3.4 更新分组信息
- **URL**: `/api/groups/{id}/`
- **方法**: `PUT` 或 `PATCH`
- **权限**: 允许任何用户访问 (默认 AllowAny)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: application/json
```
- **请求体示例** (PATCH 方法可只包含部分字段):
```json
{
  "name": "人物肖像",
  "description": "人物肖像照片分组"
}
```
- **成功响应**: `200 OK`

#### 3.5 删除分组
- **URL**: `/api/groups/{id}/`
- **方法**: `DELETE`
- **权限**: 允许任何用户访问 (默认 AllowAny)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `204 No Content`

### 4. 首页布局管理 API

#### 4.1 获取用户布局列表
- **URL**: `/api/layouts/`
- **方法**: `GET`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `200 OK`
```json
[
  {
    "id": 1,
    "name": "默认布局",
    "is_active": true,
    "config": {
      "columns": 3,
      "featured_images": [1, 2, 3],
      "featured_groups": [1],
      "show_recent": true,
      "recent_count": 6,
      "image_spacing": 8,
      "grid_padding": 16
    },
    "created_at": "2025-05-14T10:30:00Z",
    "updated_at": "2025-05-14T10:30:00Z"
  }
]
```

#### 4.2 获取当前激活布局
- **URL**: `/api/layouts/active/`
- **方法**: `GET`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `200 OK`
```json
{
  "id": 1,
  "name": "默认布局",
  "is_active": true,
  "config": {
    "columns": 3,
    "featured_images": [1, 2, 3],
    "featured_groups": [1],
    "show_recent": true,
    "recent_count": 6,
    "image_spacing": 8,
    "grid_padding": 16
  },
  "created_at": "2025-05-14T10:30:00Z",
  "updated_at": "2025-05-14T10:30:00Z"
}
```

#### 4.3 创建新布局
- **URL**: `/api/layouts/`
- **方法**: `POST`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: application/json
```
- **请求体示例**:
```json
{
  "name": "宽间距布局",
  "is_active": true,
  "config": {
    "columns": 2,
    "featured_images": [5, 8],
    "featured_groups": [2],
    "show_recent": true,
    "recent_count": 4,
    "image_spacing": 16,
    "grid_padding": 24
  }
}
```
- **成功响应**: `201 Created`

#### 4.4 更新布局
- **URL**: `/api/layouts/{id}/`
- **方法**: `PUT` 或 `PATCH`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: application/json
```
- **请求体示例** (PATCH 方法可只包含部分字段):
```json
{
  "name": "更新布局名称",
  "config": {
    "columns": 4,
    "image_spacing": 12
  }
}
```
- **成功响应**: `200 OK`

#### 4.5 激活特定布局
- **URL**: `/api/layouts/{id}/activate/`
- **方法**: `POST`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `200 OK`
```json
{
  "id": 2,
  "name": "宽间距布局",
  "is_active": true,
  "config": {
    "columns": 2,
    "featured_images": [5, 8],
    "featured_groups": [2],
    "show_recent": true,
    "recent_count": 4,
    "image_spacing": 16,
    "grid_padding": 24
  },
  "created_at": "2025-05-15T10:30:00Z",
  "updated_at": "2025-05-15T11:30:00Z"
}
```

#### 4.6 更新布局间距设置
- **URL**: `/api/layouts/{id}/update_spacing/`
- **方法**: `PATCH`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
Content-Type: application/json
```
- **请求体示例**:
```json
{
  "image_spacing": 20,
  "grid_padding": 30
}
```
- **成功响应**: `200 OK`

#### 4.7 删除布局
- **URL**: `/api/layouts/{id}/`
- **方法**: `DELETE`
- **权限**: 仅限已认证用户 (IsAuthenticated)
- **请求头**: 
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...
```
- **成功响应**: `204 No Content`

## 开发指南

### 关键配置信息
- Django REST Framework 提供了 API 功能
- JWT 认证 (djangorestframework-simplejwt) 提供了用户认证
- 数据库使用 MySQL
- 图片存储在服务器的 `/media` 目录

### 文件结构
- `/api` - API 应用目录
  - `models.py` - 数据模型 (Image, Group, HomeLayout)
  - `serializers.py` - API 序列化器
  - `views.py` - API 视图和逻辑
  - `urls.py` - API 路由配置
- `/photo_gallery` - 项目配置目录
  - `settings.py` - 项目设置
  - `urls.py` - 主 URL 配置

## 许可证

MIT
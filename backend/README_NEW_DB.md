# 创建新数据库说明

如果您希望直接创建一个新的数据库而不进行迁移，可以使用以下方法：

## 方法一：使用初始化脚本（推荐）

1. 运行初始化脚本
```bash
cd backend
python init_db.py
```

这个脚本会：
- 删除现有的数据库文件（如果存在）
- 创建新的数据库表
- 创建默认管理员账户（用户名：admin，密码：admin123）

## 方法二：手动删除并重新初始化

1. 删除现有数据库文件
```bash
# 对于SQLite
rm app.db
```

2. 运行应用程序（会自动创建新数据库）
```bash
python run.py
```

3. 创建管理员账户
```bash
python run.py init-admin
```

## 配置说明

初始化脚本会自动读取.env文件中的配置：

### 数据库配置
- `USE_POSTGRES` - 是否使用PostgreSQL数据库（true/false）
- `POSTGRES_USER` - PostgreSQL用户名
- `POSTGRES_PASSWORD` - PostgreSQL密码
- `POSTGRES_DB` - PostgreSQL数据库名
- `POSTGRES_HOST` - PostgreSQL主机地址
- `POSTGRES_PORT` - PostgreSQL端口

### 其他配置
- `UPLOAD_FOLDER` - 文件上传目录
- `SOFTWARE_STORAGE` - 软件存储目录

确保您的.env文件中已正确配置这些参数。脚本会根据USE_POSTGRES的值自动选择使用SQLite或PostgreSQL。

## 初始管理员账户

无论使用哪种方法，初始管理员账户为：
- 用户名：admin
- 密码：admin123

## 注意事项

1. 初始化数据库会删除所有现有数据
2. 确保在初始化前备份重要数据
3. 初始化后请立即修改默认密码
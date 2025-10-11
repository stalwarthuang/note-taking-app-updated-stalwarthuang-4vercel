# Vercel 部署指南

## PostgreSQL 数据库配置

本项目已配置为支持 PostgreSQL 数据库，可以在 Vercel 上部署。

### 在 Vercel 上部署步骤

1. **连接 PostgreSQL 数据库**
   - 在 Vercel 项目的 Storage 选项卡中，您已经创建了 PostgreSQL 数据库
   - Vercel 会自动设置环境变量 `POSTGRES_URL`
   - 应用会自动检测并使用这个环境变量

2. **环境变量**
   - Vercel 会自动提供以下环境变量：
     - `POSTGRES_URL`: 完整的数据库连接 URL
     - `POSTGRES_URL_NON_POOLING`: 非连接池的数据库 URL
   - 本应用已配置为自动检测 `DATABASE_URL` 或 `POSTGRES_URL`

3. **本地开发**
   - 如果不设置任何数据库环境变量，应用会自动使用 SQLite（`database/app.db`）
   - 如果需要本地测试 PostgreSQL，创建 `.env` 文件并设置：
     ```
     DATABASE_URL=postgresql://username:password@host:port/database
     ```

### 数据库 URL 格式

PostgreSQL 连接 URL 格式：
```
postgresql://username:password@host:port/database
```

Vercel 提供的 URL 可能是 `postgres://` 开头，代码会自动转换为 SQLAlchemy 需要的 `postgresql://` 格式。

### 代码修改说明

1. **requirements.txt**: 添加了 `psycopg2-binary` PostgreSQL 驱动
2. **src/main.py**: 更新了数据库配置逻辑
   - 优先使用环境变量中的 PostgreSQL URL
   - 自动处理 URL 格式转换
   - 本地开发自动降级到 SQLite

### 部署后初始化

首次部署后，数据库表会自动创建（通过 `db.create_all()`）。

### 常见问题

**Q: 如何查看 Vercel 的数据库连接信息？**
A: 在 Vercel 项目设置 -> Storage -> 选择您的 PostgreSQL 数据库 -> 查看连接信息

**Q: 本地如何测试 PostgreSQL？**
A: 创建 `.env` 文件，设置 `DATABASE_URL`，并运行 `python -m src.main`

**Q: 数据库表没有创建？**
A: 检查 Vercel 的日志，确认 `db.create_all()` 已执行且没有错误


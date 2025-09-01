# 🐳 Docker 一键部署指南

超简单的 Docker 部署方式，3分钟搞定！

## 📋 前置要求

- [x] 安装 Docker Desktop（Windows/Mac）或 Docker（Linux）
- [x] 确保 Docker 服务正在运行

## 🚀 一键部署

### Windows 用户

1. **配置环境变量**
   ```bash
   # 复制配置文件
   copy .env.example .env
   
   # 编辑 .env 文件，填入你的配置
   notepad .env
   ```

2. **一键启动**
   ```bash
   # 双击运行部署脚本
   deploy.bat
   
   # 或命令行运行
   .\deploy.bat
   ```

### Linux/Mac 用户

1. **配置环境变量**
   ```bash
   # 复制配置文件
   cp .env.example .env
   
   # 编辑配置文件
   nano .env
   ```

2. **一键启动**
   ```bash
   # 给脚本执行权限
   chmod +x deploy.sh
   
   # 运行部署脚本
   ./deploy.sh
   ```

## ⚙️ 配置说明

编辑 `.env` 文件，只需要填写这几个必要参数：

```env
# 必填配置
BOT_TOKEN=你的Telegram机器人Token
DANMAKU_API_KEY=弹幕API密钥
TMDB_API_KEY=TMDB API密钥

# 管理员用户ID（可选）
ADMIN_USER_IDS=123456789,987654321
```

### 如何获取 Token？

1. **BOT_TOKEN**: 在 Telegram 中搜索 @BotFather，创建新机器人获取
2. **DANMAKU_API_KEY**: 从弹幕系统管理后台获取
3. **TMDB_API_KEY**: 在 [TMDB官网](https://www.themoviedb.org/settings/api) 注册获取
4. **ADMIN_USER_IDS**: 在 Telegram 中搜索 @userinfobot 获取你的用户ID

## 🎯 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码后重新部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📊 服务监控

部署成功后，你可以：

- **查看日志**: `docker-compose logs -f telegram-bot`
- **进入容器**: `docker-compose exec telegram-bot bash`
- **检查数据**: `ls -la data/` （查看数据库文件）

## 🔧 故障排除

### 常见问题

**Q: 服务无法启动？**
A: 检查 `.env` 配置是否正确，确保所有必要的 Token 都已填写

**Q: 机器人不响应？**
A: 检查 BOT_TOKEN 是否正确，网络是否能访问 Telegram

**Q: 弹幕发送失败？**  
A: 检查 DANMAKU_API_KEY 和弹幕服务器地址是否正确

**Q: Docker 构建失败？**
A: 确保网络连接正常，可以尝试使用国内镜像源

### 查看详细日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs telegram-bot

# 实时跟踪日志
docker-compose logs -f --tail=100
```

### 重置服务

```bash
# 完全清理并重新部署
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

## 🎉 部署成功

看到这个消息说明部署成功：
```
✅ 服务启动成功！
```

现在你可以在 Telegram 中找到你的机器人并开始使用了！

发送 `/start` 给机器人开始体验所有功能：
- 🎯 弹幕管理
- 🎬 电影搜索  
- 📋 队列管理
- 🛡️ 内容审核
- 📊 数据统计

---

**提示**: 首次部署可能需要几分钟时间下载 Docker 镜像，请耐心等待。
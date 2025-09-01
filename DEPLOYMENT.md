# VPS 部署教程

本教程将指导您在 VPS 上部署 Telegram 弹幕控制机器人。

## 📋 前置要求

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **内存**: 最低 1GB RAM（推荐 2GB+）
- **存储**: 最低 10GB 可用空间
- **网络**: 稳定的互联网连接，可访问 Telegram API

### 必要软件
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+

## 🛠️ 服务器准备

### 1. 更新系统
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
# 或对于较新版本
sudo dnf update -y
```

### 2. 安装 Docker

#### Ubuntu/Debian 系统
```bash
# 移除旧版本
sudo apt-get remove docker docker-engine docker.io containerd runc

# 安装依赖
sudo apt-get update
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

#### CentOS/RHEL 系统
```bash
# 移除旧版本
sudo yum remove docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine

# 安装 yum-utils
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. 安装 Docker Compose（如果未包含）
```bash
# 下载最新版本的 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 4. 配置用户权限
```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或运行以下命令
newgrp docker

# 验证是否可以运行 docker 命令
docker run hello-world
```

## 📦 项目部署

### 1. 创建项目目录
```bash
# 创建项目目录
mkdir -p ~/telegram-danmaku-bot
cd ~/telegram-danmaku-bot
```

### 2. 获取项目代码

#### 方式1: 使用 Git（推荐）
```bash
# 克隆项目仓库
git clone <your-repository-url> .

# 如果没有 Git 仓库，可以使用下面的方法
```

#### 方式2: 手动上传
```bash
# 在本地压缩项目文件，然后上传到服务器
# 可以使用 scp 命令上传
scp -r /path/to/local/project/* user@your-server-ip:~/telegram-danmaku-bot/
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量文件
nano .env  # 或使用 vim .env
```

#### 环境变量配置说明
```bash
# Telegram Bot Token（必填）
BOT_TOKEN=8214946947:AAE6LQ6ALn3Ae06Y0HRytrlhW2t-1yHRuj8

# 弹幕 API 配置（必填）
DANMAKU_API_KEY=jt8kjydaKqnn0y6pjr0UiX273PZKXWFq
DANMAKU_BASE_URL=http://154.12.85.19:7768

# TMDB API 配置（必填）
TMDB_API_KEY=6e502611fd4c1608f8211ead0b864312
TMDB_BASE_URL=https://api.themoviedb.org/3
TMDB_IMAGE_URL=https://image.tmdb.org

# 数据库配置
DATABASE_URL=sqlite:///data/bot.db

# 日志配置
LOG_LEVEL=INFO

# 管理员用户ID（可选，多个用逗号分隔）
ADMIN_USER_IDS=123456789,987654321
```

### 4. 创建必要目录
```bash
# 创建数据和日志目录
mkdir -p data logs

# 设置权限
chmod 755 data logs
```

### 5. 启动服务

#### 方式1: 使用部署脚本（推荐）
```bash
# 给部署脚本添加执行权限
chmod +x deploy.sh

# 启动服务
./deploy.sh start
```

#### 方式2: 直接使用 Docker Compose
```bash
# 构建并启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f telegram-bot
```

## 🔧 服务管理

### 常用命令

#### 使用部署脚本
```bash
# 启动服务
./deploy.sh start

# 停止服务
./deploy.sh stop

# 重启服务
./deploy.sh restart

# 查看日志
./deploy.sh logs

# 查看状态
./deploy.sh status

# 更新服务
./deploy.sh update

# 备份数据
./deploy.sh backup

# 清理资源
./deploy.sh cleanup
```

#### 直接使用 Docker Compose
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f telegram-bot

# 查看状态
docker-compose ps

# 更新服务
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 日志管理
```bash
# 实时查看日志
docker-compose logs -f telegram-bot

# 查看最近100行日志
docker-compose logs --tail=100 telegram-bot

# 查看特定时间段的日志
docker-compose logs --since="2024-01-01T00:00:00" telegram-bot

# 查看日志文件
tail -f logs/bot.log
```

## 🔒 安全配置

### 1. 防火墙配置
```bash
# Ubuntu/Debian (UFW)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443

# CentOS/RHEL (firewalld)
sudo systemctl start firewalld
sudo systemctl enable firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. SSH 安全加固
```bash
# 编辑 SSH 配置
sudo nano /etc/ssh/sshd_config

# 建议的安全配置：
# Port 22222  # 更改默认端口
# PermitRootLogin no  # 禁止 root 登录
# PasswordAuthentication no  # 禁用密码登录（使用密钥）
# MaxAuthTries 3  # 限制认证尝试次数

# 重启 SSH 服务
sudo systemctl restart sshd
```

### 3. 定期更新
```bash
# 创建自动更新脚本
cat > ~/update-bot.sh << 'EOF'
#!/bin/bash
cd ~/telegram-danmaku-bot
git pull
./deploy.sh update
EOF

chmod +x ~/update-bot.sh

# 添加定时任务（每周更新）
(crontab -l 2>/dev/null; echo "0 2 * * 0 ~/update-bot.sh") | crontab -
```

## 📊 监控和维护

### 1. 系统监控
```bash
# 查看系统资源使用
htop
# 或
top

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看 Docker 容器资源使用
docker stats
```

### 2. 服务健康检查
```bash
# 检查容器状态
docker-compose ps

# 检查服务端口
netstat -tlnp | grep docker

# 测试机器人响应
# 在 Telegram 中发送 /start 命令测试
```

### 3. 数据备份
```bash
# 手动备份
./deploy.sh backup

# 设置自动备份（每日凌晨3点）
(crontab -l 2>/dev/null; echo "0 3 * * * cd ~/telegram-danmaku-bot && ./deploy.sh backup") | crontab -

# 备份到远程服务器（可选）
rsync -avz ~/telegram-danmaku-bot/backups/ user@backup-server:/backups/telegram-bot/
```

## 🚨 故障排除

### 常见问题及解决方案

#### 1. 机器人无响应
```bash
# 检查容器状态
docker-compose ps

# 查看日志
docker-compose logs telegram-bot

# 重启服务
./deploy.sh restart
```

#### 2. API 连接失败
```bash
# 检查网络连接
ping api.telegram.org
ping 154.12.85.19

# 检查环境变量
cat .env

# 测试 API 连接
curl -X GET "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"
```

#### 3. 数据库问题
```bash
# 检查数据目录权限
ls -la data/

# 重建数据库
docker-compose down
rm -f data/bot.db
docker-compose up -d
```

#### 4. 磁盘空间不足
```bash
# 清理 Docker 资源
./deploy.sh cleanup

# 清理日志文件
sudo journalctl --vacuum-time=7d

# 清理系统缓存
sudo apt clean  # Ubuntu/Debian
sudo yum clean all  # CentOS/RHEL
```

### 日志分析
```bash
# 查找错误日志
grep -i "error" logs/bot.log

# 查找警告信息
grep -i "warning" logs/bot.log

# 统计日志级别
awk '{print $3}' logs/bot.log | sort | uniq -c
```

## 🔄 更新和维护

### 1. 应用更新
```bash
# 更新代码
git pull

# 更新服务
./deploy.sh update
```

### 2. 系统更新
```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
sudo yum update -y  # CentOS/RHEL

# 更新 Docker
sudo apt install docker-ce docker-ce-cli containerd.io  # Ubuntu/Debian
sudo yum update docker-ce docker-ce-cli containerd.io  # CentOS/RHEL
```

### 3. 配置调优

#### 内存优化
```bash
# 编辑 docker-compose.yml，添加资源限制
services:
  telegram-bot:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

#### 性能监控
```bash
# 安装监控工具
sudo apt install htop iotop nethogs  # Ubuntu/Debian
sudo yum install htop iotop nethogs  # CentOS/RHEL

# 监控 Docker 容器
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
```

## 📞 技术支持

如果在部署过程中遇到问题，请：

1. 检查本文档的故障排除部分
2. 查看项目日志文件
3. 检查 GitHub Issues
4. 联系项目维护者

---

**注意**: 请确保所有敏感信息（如 Token、API 密钥）的安全性，不要在公开场所泄露这些信息。
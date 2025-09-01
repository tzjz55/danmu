# Telegram 弹幕控制机器人

一个基于 Telegram Bot API 的弹幕系统控制机器人，用于通过 Telegram 界面远程控制 Misaka 弹幕系统。

## 功能特点

- 🎮 直观的按钮式交互界面
- 📊 实时服务器状态监控
- 🎯 弹幕内容管理和控制
- 🎬 TMDB 电影信息查询
- 👥 用户权限管理系统
- 📋 操作日志记录
- 🐳 Docker 容器化部署

## 快速开始

<<<<<<< HEAD
### 方法一：Docker 一键部署（推荐）

1. 安装 Docker Desktop
2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

3. 一键部署
```bash
# Windows
.\deploy.bat

# Linux/Mac
./deploy.sh
```

详细部署指南请查看 [DOCKER_DEPLOY.md](DOCKER_DEPLOY.md)

### 方法二：本地开发
=======
### 本地开发
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103

1. 配置环境变量
```bash
cp .env.example .env
<<<<<<< HEAD
# 编辑 .env 文件
=======
# 编辑 .env 文件，填入相应的 API 密钥
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
```

2. 快速启动（自动安装依赖）
```bash
python start.py
```

3. 或手动启动
```bash
pip install -r requirements.txt
python bot.py
```

<<<<<<< HEAD
=======
4. 测试项目
```bash
python test.py
```

### Docker 部署

1. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件
```

2. 构建并启动
```bash
docker-compose up -d
```

>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
## 项目结构

```
danmu/
├── bot.py                  # 主应用程序
├── config.py              # 配置管理
├── start.py               # 快速启动脚本
├── test.py                # 项目测试脚本
├── requirements.txt        # Python 依赖
├── docker-compose.yml     # Docker Compose 配置
├── Dockerfile             # Docker 镜像配置
├── deploy.sh              # 部署脚本
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略文件
├── DEPLOYMENT.md          # 部署教程
├── handlers/              # 处理器模块
│   ├── __init__.py
│   ├── commands.py        # 命令处理器
│   └── callbacks.py       # 回调处理器
├── clients/               # API 客户端
│   ├── __init__.py
│   ├── danmaku_client.py  # 弹幕 API 客户端
│   └── tmdb_client.py     # TMDB API 客户端
├── managers/              # 管理器模块
│   ├── __init__.py
│   └── user_manager.py    # 用户管理器
├── utils/                 # 工具模块
│   ├── __init__.py
│   └── keyboards.py       # 键盘布局
├── data/                  # 数据目录
│   └── bot.db            # SQLite 数据库
└── logs/                  # 日志目录
    └── bot.log           # 应用日志
```

## 配置说明

主要配置项（在 `.env` 文件中设置）：

```bash
BOT_TOKEN=your_telegram_bot_token
DANMAKU_API_KEY=your_danmaku_api_key
TMDB_API_KEY=your_tmdb_api_key
ADMIN_USER_IDS=comma_separated_admin_user_ids
```

## 部署教程

详细的 VPS 部署教程请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

## API 文档

- [弹幕控制 API](http://154.12.85.19:7768/api/control/docs)
- [TMDB API](https://developers.themoviedb.org/3)

## 许可证

MIT License
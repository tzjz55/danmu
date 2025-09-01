@echo off
chcp 65001 >nul

echo 🚀 弹幕机器人 Docker 一键部署
echo ================================

REM 检查环境变量文件
if not exist ".env" (
    echo ❌ 未找到 .env 配置文件
    echo 请先创建 .env 文件并配置以下变量：
    echo BOT_TOKEN=你的机器人token
    echo DANMAKU_API_KEY=弹幕API密钥
    echo TMDB_API_KEY=TMDB API密钥
    echo ADMIN_USER_IDS=管理员用户ID
    pause
    exit /b 1
)

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否可用
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose 不可用，请确保 Docker Desktop 正常运行
    pause
    exit /b 1
)

echo ✅ 环境检查通过

REM 创建必要目录
if not exist "data" mkdir data
if not exist "logs" mkdir logs
echo ✅ 创建数据目录

REM 停止现有容器
echo 🛑 停止现有容器...
docker-compose down >nul 2>&1

REM 构建并启动
echo 🔨 构建镜像...
docker-compose build

echo 🚀 启动服务...
docker-compose up -d

REM 等待服务启动
echo 等待服务启动...
timeout /t 5 /nobreak >nul

REM 检查服务状态
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ 服务启动成功！
    echo.
    echo 📊 服务状态：
    docker-compose ps
    echo.
    echo 📋 查看日志：
    echo   docker-compose logs -f
    echo.
    echo 🛑 停止服务：
    echo   docker-compose down
    echo.
    echo 🔄 重启服务：
    echo   docker-compose restart
) else (
    echo ❌ 服务启动失败，请检查日志：
    docker-compose logs
    pause
    exit /b 1
)

pause
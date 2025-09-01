#!/bin/bash

<<<<<<< HEAD
# 弹幕机器人一键部署脚本

echo "🚀 弹幕机器人 Docker 一键部署"
echo "================================"

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "❌ 未找到 .env 配置文件"
    echo "请先创建 .env 文件并配置以下变量："
    echo "BOT_TOKEN=你的机器人token"
    echo "DANMAKU_API_KEY=弹幕API密钥"  
    echo "TMDB_API_KEY=TMDB API密钥"
    echo "ADMIN_USER_IDS=管理员用户ID"
    exit 1
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ 环境检查通过"

# 创建必要目录
mkdir -p data logs
echo "✅ 创建数据目录"

# 停止现有容器
echo "🛑 停止现有容器..."
docker-compose down 2>/dev/null

# 构建并启动
echo "🔨 构建镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 检查服务状态
sleep 5
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "📊 服务状态："
    docker-compose ps
    echo ""
    echo "📋 查看日志："
    echo "  docker-compose logs -f"
    echo ""
    echo "🛑 停止服务："
    echo "  docker-compose down"
    echo ""
    echo "🔄 重启服务："
    echo "  docker-compose restart"
else
    echo "❌ 服务启动失败，请检查日志："
    docker-compose logs
    exit 1
fi

=======
>>>>>>> d7713b91f7befb22e88fb9bbcf3ab5a17dfa2103
# 弹幕机器人部署脚本
# 使用方法: ./deploy.sh [start|stop|restart|update|logs|status]

set -e

PROJECT_NAME="danmaku-telegram-bot"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查环境
check_requirements() {
    print_info "检查运行环境..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装"
        exit 1
    fi
    
    # 检查环境变量文件
    if [ ! -f "$ENV_FILE" ]; then
        print_error "环境变量文件 $ENV_FILE 不存在"
        print_info "请复制 .env.example 到 .env 并配置相关参数"
        exit 1
    fi
    
    print_success "环境检查通过"
}

# 启动服务
start_service() {
    print_info "启动 $PROJECT_NAME 服务..."
    docker-compose -f $COMPOSE_FILE up -d
    
    if [ $? -eq 0 ]; then
        print_success "服务启动成功"
        print_info "使用 './deploy.sh logs' 查看日志"
        print_info "使用 './deploy.sh status' 查看状态"
    else
        print_error "服务启动失败"
        exit 1
    fi
}

# 停止服务
stop_service() {
    print_info "停止 $PROJECT_NAME 服务..."
    docker-compose -f $COMPOSE_FILE down
    
    if [ $? -eq 0 ]; then
        print_success "服务已停止"
    else
        print_error "服务停止失败"
        exit 1
    fi
}

# 重启服务
restart_service() {
    print_info "重启 $PROJECT_NAME 服务..."
    stop_service
    sleep 2
    start_service
}

# 更新服务
update_service() {
    print_info "更新 $PROJECT_NAME 服务..."
    
    # 停止服务
    docker-compose -f $COMPOSE_FILE down
    
    # 重新构建镜像
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    # 启动服务
    docker-compose -f $COMPOSE_FILE up -d
    
    # 清理无用镜像
    docker image prune -f
    
    print_success "服务更新完成"
}

# 查看日志
show_logs() {
    print_info "显示 $PROJECT_NAME 日志..."
    docker-compose -f $COMPOSE_FILE logs -f --tail=50 telegram-bot
}

# 查看状态
show_status() {
    print_info "显示 $PROJECT_NAME 状态..."
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    print_info "容器资源使用情况:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# 备份数据
backup_data() {
    print_info "备份数据..."
    
    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # 备份数据文件
    if [ -d "data" ]; then
        cp -r data "$backup_dir/"
        print_success "数据备份到: $backup_dir/data"
    fi
    
    # 备份配置文件
    cp .env "$backup_dir/" 2>/dev/null || true
    cp docker-compose.yml "$backup_dir/" 2>/dev/null || true
    
    print_success "备份完成: $backup_dir"
}

# 清理资源
cleanup() {
    print_info "清理 Docker 资源..."
    
    # 停止服务
    docker-compose -f $COMPOSE_FILE down
    
    # 清理无用容器
    docker container prune -f
    
    # 清理无用镜像
    docker image prune -f
    
    # 清理无用卷
    docker volume prune -f
    
    print_success "清理完成"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [COMMAND]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  update    更新服务（重新构建镜像）"
    echo "  logs      查看日志"
    echo "  status    查看状态"
    echo "  backup    备份数据"
    echo "  cleanup   清理 Docker 资源"
    echo "  help      显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start    # 启动服务"
    echo "  $0 logs     # 查看日志"
}

# 主函数
main() {
    case "$1" in
        start)
            check_requirements
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            check_requirements
            restart_service
            ;;
        update)
            check_requirements
            update_service
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        backup)
            backup_data
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
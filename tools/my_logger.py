# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
日志配置模块
提供彩色日志输出、进度显示等功能
"""

import os
import sys
from datetime import datetime
from typing import Optional

from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

# 日志路径
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILENAME = os.path.join(log_path, "log_all_{}.log".format(datetime.now().strftime('%Y%m%d')))
LOG_ERROR_FILENAME = os.path.join(log_path, "log_error_{}.log".format(datetime.now().strftime('%Y%m%d')))

# 全局控制台实例
console = Console()


class RichLogHandler:
    """自定义 Rich 日志处理器"""
    
    LEVEL_STYLES = {
        "DEBUG": "dim",
        "INFO": "cyan",
        "SUCCESS": "bold green",
        "WARNING": "bold yellow",
        "ERROR": "bold red",
        "CRITICAL": "bold white on red"
    }
    
    def write(self, message):
        record = message.record
        level = record["level"].name
        style = self.LEVEL_STYLES.get(level, "")
        
        # 格式化时间
        time_str = record["time"].strftime("%H:%M:%S.%f")[:-3]
        
        # 构建消息
        msg = record["message"]
        
        # 使用 Rich 输出
        console.print(
            f"[dim]{time_str}[/dim] | "
            f"[{style}]{level:^8}[/{style}] | "
            f"{msg}"
        )


def setup_logger(debug: bool = False):
    """
    设置日志配置
    
    Args:
        debug: 是否开启调试模式
    """
    # 确保日志目录存在
    os.makedirs(log_path, exist_ok=True)
    
    # 日志格式
    file_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<cyan>{process.name}</cyan>:<cyan>{thread.name}</cyan> - "
        "<level>{message}</level>"
    )
    
    console_format = (
        "<green>{time:HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<level>{message}</level>"
    )
    
    # 移除默认处理器
    logger.remove()
    
    # 文件日志 - 全部日志
    logger.add(
        LOG_FILENAME,
        format=file_format,
        rotation='50 MB',
        retention='7 days',
        level="DEBUG",
        encoding='utf8',
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # 文件日志 - 错误日志
    logger.add(
        LOG_ERROR_FILENAME,
        format=file_format,
        rotation='50 MB',
        retention='7 days',
        level="ERROR",
        encoding='utf8',
        enqueue=True,
        backtrace=True,
        diagnose=True
    )
    
    # 控制台日志
    log_level = "DEBUG" if debug else "INFO"
    logger.add(
        sink=sys.stdout,
        format=console_format,
        level=log_level,
        colorize=True
    )
    
    logger.info("日志系统初始化完成")


class ProgressManager:
    """进度管理器，用于显示抢购进度"""
    
    def __init__(self):
        self.progress: Optional[Progress] = None
        self.live: Optional[Live] = None
        self.task_id = None
        
    def start_countdown(self, total_seconds: int, description: str = "倒计时"):
        """开始倒计时显示"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        )
        self.task_id = self.progress.add_task(description, total=total_seconds)
        self.live = Live(self.progress, console=console, refresh_per_second=10)
        self.live.start()
        
    def update_countdown(self, completed: int):
        """更新倒计时进度"""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, completed=completed)
    
    def stop_countdown(self):
        """停止倒计时显示"""
        if self.live:
            self.live.stop()
            self.progress = None
            self.task_id = None


class StatusDisplay:
    """状态显示管理器"""
    
    @staticmethod
    def show_status(title: str, status: str, style: str = "green"):
        """显示状态面板"""
        panel = Panel(
            Text(status, justify="center"),
            title=title,
            border_style=style
        )
        console.print(panel)
    
    @staticmethod
    def show_success(message: str):
        """显示成功消息"""
        console.print(f"[bold green]✅ {message}[/bold green]")
        
    @staticmethod
    def show_error(message: str):
        """显示错误消息"""
        console.print(f"[bold red]❌ {message}[/bold red]")
        
    @staticmethod
    def show_warning(message: str):
        """显示警告消息"""
        console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")
        
    @staticmethod
    def show_info(message: str):
        """显示信息消息"""
        console.print(f"[bold blue]ℹ️ {message}[/bold blue]")


# 全局进度管理器
progress_manager = ProgressManager()
status_display = StatusDisplay()
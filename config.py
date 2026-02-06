# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
配置文件解析和验证模块
提供配置读取、验证和默认值处理功能
"""

import os
from configparser import ConfigParser
from dataclasses import dataclass, field
from typing import Optional, List
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


@dataclass
class UserConfig:
    """用户账号配置"""
    name: str = ""
    password: str = ""


@dataclass
class ProductConfig:
    """商品配置"""
    name: str = ""
    id: str = ""
    color: str = ""
    version: str = ""
    payment: str = "全款购买"
    sets: str = ""


@dataclass
class BrowserConfig:
    """浏览器配置"""
    type: str = "chrome"
    driver_path: str = ""
    headless: bool = False
    user_agent: str = ""
    proxy: str = ""  # 新增代理支持


@dataclass
class ProcessConfig:
    """处理配置"""
    thread: int = 1
    interval: float = 0.001
    retry_times: int = 3
    timeout: int = 30  # 新增超时配置


@dataclass 
class NotifyConfig:
    """通知配置"""
    enable_sound: bool = True  # 抢购成功后是否播放声音
    enable_email: bool = False  # 是否发送邮件通知
    email_to: str = ""
    email_from: str = ""
    email_password: str = ""


@dataclass
class AppConfig:
    """应用总配置"""
    user: UserConfig = field(default_factory=UserConfig)
    product: ProductConfig = field(default_factory=ProductConfig)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    process: ProcessConfig = field(default_factory=ProcessConfig)
    notify: NotifyConfig = field(default_factory=NotifyConfig)


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class Config:
    """配置管理类，支持配置验证和美化输出"""
    
    SUPPORTED_BROWSERS = ['chrome', 'firefox', 'edge', 'safari']
    MAX_THREADS = 20
    MIN_INTERVAL = 0.001
    
    def __init__(self, filename: str, encoding: str = "utf-8"):
        logger.info("开始解析配置文件")
        self.filename = filename
        self.encoding = encoding
        self.config = ConfigParser()
        self.app_config: Optional[AppConfig] = None
        
        if not os.path.exists(filename):
            raise ConfigValidationError(f"配置文件不存在: {filename}")
        
        self.config.read(filename, encoding)
        self._parse_config()
        logger.info("配置文件解析完成")

    def _parse_config(self):
        """解析配置到数据类"""
        self.app_config = AppConfig(
            user=UserConfig(
                name=self.get("user", "name", ""),
                password=self.get("user", "password", "")
            ),
            product=ProductConfig(
                name=self.get("product", "name", ""),
                id=self.get("product", "id", ""),
                color=self.get("product", "color", ""),
                version=self.get("product", "version", ""),
                payment=self.get("product", "payment", "全款购买"),
                sets=self.get("product", "sets", "")
            ),
            browser=BrowserConfig(
                type=self.get("browser", "type", "chrome"),
                driver_path=self.get("browser", "driverPath", ""),
                headless=self.getboolean("browser", "headless", False),
                user_agent=self.get("browser", "userAgent", ""),
                proxy=self.get("browser", "proxy", "")
            ),
            process=ProcessConfig(
                thread=self.getint("process", "thread", 1),
                interval=self.getfloat("process", "interval", 0.001),
                retry_times=self.getint("process", "retryTimes", 3),
                timeout=self.getint("process", "timeout", 30)
            ),
            notify=NotifyConfig(
                enable_sound=self.getboolean("notify", "enableSound", True),
                enable_email=self.getboolean("notify", "enableEmail", False),
                email_to=self.get("notify", "emailTo", ""),
                email_from=self.get("notify", "emailFrom", ""),
                email_password=self.get("notify", "emailPassword", "")
            )
        )

    def get(self, section: str, option: str, default_value: str = None) -> str:
        """获取字符串配置"""
        try:
            return self.config.get(section, option)
        except:
            return default_value if default_value is not None else ""

    def getboolean(self, section: str, option: str, default_value: bool = None) -> bool:
        """获取布尔配置"""
        try:
            return self.config.getboolean(section, option)
        except:
            return default_value if default_value is not None else False

    def getint(self, section: str, option: str, default_value: int = None) -> int:
        """获取整数配置"""
        try:
            return self.config.getint(section, option)
        except:
            return default_value if default_value is not None else 0

    def getfloat(self, section: str, option: str, default_value: float = None) -> float:
        """获取浮点数配置"""
        try:
            return self.config.getfloat(section, option)
        except:
            return default_value if default_value is not None else 0.0

    def validate(self) -> List[str]:
        """验证配置有效性，返回错误列表"""
        errors = []
        warnings = []
        
        # 验证用户配置
        if not self.app_config.user.name:
            errors.append("❌ 用户名不能为空")
        if not self.app_config.user.password:
            errors.append("❌ 密码不能为空")
        
        # 验证商品配置
        if not self.app_config.product.id:
            errors.append("❌ 商品ID不能为空")
        if not self.app_config.product.color:
            warnings.append("⚠️ 未配置商品颜色，将使用默认选项")
        if not self.app_config.product.version:
            warnings.append("⚠️ 未配置商品版本，将使用默认选项")
        
        # 验证浏览器配置
        if self.app_config.browser.type not in self.SUPPORTED_BROWSERS:
            errors.append(f"❌ 不支持的浏览器类型: {self.app_config.browser.type}")
        
        if self.app_config.browser.headless and not self.app_config.browser.user_agent:
            warnings.append("⚠️ 无头模式建议配置 userAgent")
        
        # 验证处理配置
        if self.app_config.process.thread < 1:
            errors.append("❌ 线程数不能小于1")
        elif self.app_config.process.thread > self.MAX_THREADS:
            warnings.append(f"⚠️ 线程数超过{self.MAX_THREADS}，已自动调整")
            self.app_config.process.thread = self.MAX_THREADS
        
        if self.app_config.process.interval < self.MIN_INTERVAL:
            warnings.append(f"⚠️ 间隔时间过小，已调整为{self.MIN_INTERVAL}秒")
            self.app_config.process.interval = self.MIN_INTERVAL
        
        # 打印警告
        for warning in warnings:
            logger.warning(warning)
        
        return errors

    def display(self):
        """美化显示配置信息"""
        table = Table(title="🔧 当前配置信息", show_header=True, header_style="bold magenta")
        table.add_column("配置项", style="cyan", width=20)
        table.add_column("值", style="green")
        
        # 用户配置
        table.add_row("👤 用户名", self.app_config.user.name)
        table.add_row("🔑 密码", "*" * len(self.app_config.user.password))
        
        # 商品配置
        table.add_row("📦 商品名称", self.app_config.product.name)
        table.add_row("🆔 商品ID", self.app_config.product.id)
        table.add_row("🎨 颜色", self.app_config.product.color)
        table.add_row("📐 版本", self.app_config.product.version)
        table.add_row("💰 支付方式", self.app_config.product.payment)
        
        # 浏览器配置
        table.add_row("🌐 浏览器", self.app_config.browser.type)
        table.add_row("👻 无头模式", "是" if self.app_config.browser.headless else "否")
        
        # 处理配置
        table.add_row("🧵 线程数", str(self.app_config.process.thread))
        table.add_row("⏱️ 间隔时间", f"{self.app_config.process.interval}秒")
        
        console.print(table)

    def validate_and_display(self) -> bool:
        """验证并显示配置，返回是否通过验证"""
        console.print(Panel.fit("📋 [bold blue]配置验证[/bold blue]"))
        
        errors = self.validate()
        self.display()
        
        if errors:
            console.print("\n[bold red]配置验证失败:[/bold red]")
            for error in errors:
                console.print(f"  {error}")
            return False
        
        console.print("\n[bold green]✅ 配置验证通过[/bold green]")
        return True
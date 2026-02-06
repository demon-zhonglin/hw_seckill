# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
通用工具模块
提供文件操作、Cookie管理、通知等功能
"""

import json
import locale
import os
import sys
import platform
from typing import Optional, List, Dict, Any
from pathlib import Path
from functools import wraps
from contextlib import contextmanager
import threading
import time

from loguru import logger

import constants


def retry(max_attempts: int = 3, delay: float = 0.5, exceptions: tuple = (Exception,)):
    """
    重试装饰器
    
    Args:
        max_attempts: 最大重试次数
        delay: 重试间隔（秒）
        exceptions: 需要捕获的异常类型
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(f"{func.__name__} 第{attempt}次执行失败，{delay}秒后重试: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"{func.__name__} 执行失败，已重试{max_attempts}次")
            raise last_exception
        return wrapper
    return decorator


def get_profile_path(base_profile_path: str, browser_type: str, serial_no: int = 1) -> str:
    """
    获取浏览器配置文件路径
    
    Args:
        base_profile_path: 基础路径
        browser_type: 浏览器类型
        serial_no: 序号
    
    Returns:
        配置文件完整路径
    """
    base_browser_profile_path = os.path.join(base_profile_path, browser_type)
    profile_path = os.path.join(base_browser_profile_path, f"profile_{serial_no}")
    return profile_path


def create_directory(directory_path: str) -> bool:
    """
    创建目录（如果不存在）
    
    Args:
        directory_path: 目录路径
    
    Returns:
        是否创建成功
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败 {directory_path}: {e}")
        return False


def set_locale_chinese():
    """设置中文环境"""
    try:
        if sys.platform.startswith('win'):
            locale.setlocale(locale.LC_ALL, 'en')
            locale.setlocale(locale.LC_CTYPE, 'chinese')
        else:
            locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except Exception as e:
        logger.warning(f"设置中文环境失败: {e}")


class CookieManager:
    """Cookie 管理器"""
    
    def __init__(self, cookie_file: str = None):
        self.cookie_file = cookie_file or constants.COOKIES_FILE
        self._lock = threading.Lock()
    
    def write(self, cookies: List[Dict[str, Any]]) -> bool:
        """
        保存 Cookies
        
        Args:
            cookies: Cookie 列表
        
        Returns:
            是否保存成功
        """
        try:
            with self._lock:
                with open(self.cookie_file, 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cookies 已保存到 {self.cookie_file}")
            return True
        except Exception as e:
            logger.error(f"保存 Cookies 失败: {e}")
            return False
    
    def read(self) -> Optional[List[Dict[str, Any]]]:
        """
        读取 Cookies
        
        Returns:
            Cookie 列表或 None
        """
        try:
            with self._lock:
                if not os.path.exists(self.cookie_file):
                    return None
                with open(self.cookie_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"读取 Cookies 失败: {e}")
            return None
    
    def delete(self) -> bool:
        """
        删除 Cookie 文件
        
        Returns:
            是否删除成功
        """
        try:
            if os.path.exists(self.cookie_file):
                os.remove(self.cookie_file)
                logger.debug(f"Cookie 文件已删除: {self.cookie_file}")
            return True
        except Exception as e:
            logger.error(f"删除 Cookie 文件失败: {e}")
            return False


# 兼容旧接口
def write_cookies(cookies: List[Dict[str, Any]]):
    """保存 Cookies（兼容旧接口）"""
    CookieManager().write(cookies)


def read_cookies() -> Optional[List[Dict[str, Any]]]:
    """读取 Cookies（兼容旧接口）"""
    return CookieManager().read()


class Notifier:
    """通知管理器"""
    
    @staticmethod
    def play_sound(sound_type: str = "success"):
        """
        播放提示音
        
        Args:
            sound_type: 声音类型 (success, error, warning)
        """
        try:
            if platform.system() == "Windows":
                import winsound
                if sound_type == "success":
                    winsound.MessageBeep(winsound.MB_OK)
                elif sound_type == "error":
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                else:
                    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif platform.system() == "Darwin":  # macOS
                os.system("afplay /System/Library/Sounds/Glass.aiff")
            else:  # Linux
                os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || echo -e '\a'")
        except Exception as e:
            logger.debug(f"播放声音失败: {e}")
    
    @staticmethod
    def send_email(to: str, subject: str, body: str, 
                   from_addr: str = "", password: str = "") -> bool:
        """
        发送邮件通知
        
        Args:
            to: 收件人
            subject: 主题
            body: 正文
            from_addr: 发件人
            password: 密码
        
        Returns:
            是否发送成功
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.header import Header
            
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['From'] = from_addr
            msg['To'] = to
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 简单的 SMTP 发送（需要根据实际邮箱服务商配置）
            server = smtplib.SMTP_SSL('smtp.qq.com', 465)
            server.login(from_addr, password)
            server.sendmail(from_addr, [to], msg.as_string())
            server.quit()
            
            logger.info(f"邮件通知已发送至 {to}")
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False


class Statistics:
    """抢购统计"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self.start_time: Optional[float] = None
        self.attempt_count: int = 0
        self.success: bool = False
        self.error_count: int = 0
        self.last_error: str = ""
    
    def start(self):
        """开始统计"""
        with self._lock:
            self.start_time = time.time()
            self.attempt_count = 0
            self.success = False
            self.error_count = 0
    
    def record_attempt(self):
        """记录一次尝试"""
        with self._lock:
            self.attempt_count += 1
    
    def record_error(self, error: str):
        """记录错误"""
        with self._lock:
            self.error_count += 1
            self.last_error = error
    
    def record_success(self):
        """记录成功"""
        with self._lock:
            self.success = True
    
    def get_elapsed_time(self) -> float:
        """获取已用时间（秒）"""
        if self.start_time:
            return time.time() - self.start_time
        return 0
    
    def summary(self) -> str:
        """获取统计摘要"""
        elapsed = self.get_elapsed_time()
        result = "成功 ✅" if self.success else "失败 ❌"
        
        return (
            f"\n{'='*50}\n"
            f"📊 抢购统计\n"
            f"{'='*50}\n"
            f"结果: {result}\n"
            f"用时: {elapsed:.2f} 秒\n"
            f"尝试次数: {self.attempt_count}\n"
            f"错误次数: {self.error_count}\n"
            f"{'='*50}"
        )


# 全局实例
cookie_manager = CookieManager()
notifier = Notifier()
statistics = Statistics()


@contextmanager
def timer(description: str = "操作"):
    """
    计时器上下文管理器
    
    使用方式:
        with timer("登录"):
            do_login()
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    logger.debug(f"{description} 耗时: {elapsed:.3f}秒")


def get_system_info() -> Dict[str, str]:
    """获取系统信息"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
    }
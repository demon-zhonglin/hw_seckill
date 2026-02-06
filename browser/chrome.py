# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
Chrome 浏览器驱动模块
提供 Chrome 浏览器的配置和初始化
"""

import os
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger

from browser.browser import Browser
from config import Config
import constants


class ChromeBrowser(Browser):
    """Chrome 浏览器类"""
    
    def setting(self, config: Config = None, log_path: str = "", user_data_dir: str = "") -> webdriver.Chrome:
        """
        配置并创建 Chrome 浏览器实例
        
        Args:
            config: 配置对象
            log_path: 日志文件路径
            user_data_dir: 用户数据目录
        
        Returns:
            Chrome WebDriver 实例
        """
        options = webdriver.ChromeOptions()
        
        # 用户数据目录配置
        if user_data_dir:
            options.add_argument(f"--user-data-dir={user_data_dir}")
            options.add_argument("--profile-directory=Default")
        
        # 无头模式配置
        if config and config.getboolean("browser", "headless", False):
            options.add_argument('--headless=new')  # 使用新版无头模式
            
            # 设置 User-Agent
            default_user_agent = constants.Defaults.USER_AGENT
            user_agent = config.get("browser", "userAgent", default_user_agent)
            options.add_argument(f"user-agent={user_agent}")
            options.add_argument("--window-size=1920,1080")
        
        # 代理配置
        if config:
            proxy = config.get("browser", "proxy", "")
            if proxy:
                options.add_argument(f"--proxy-server={proxy}")
                logger.info(f"已配置代理: {proxy}")
        
        # 性能优化配置
        self._add_performance_options(options)
        
        # 安全和稳定性配置
        self._add_security_options(options)
        
        # 反自动化检测配置
        self._add_anti_detection_options(options)
        
        # 创建浏览器实例
        browser = self._create_browser(config, options, log_path)
        
        # 执行反检测脚本
        self._execute_anti_detection_scripts(browser)
        
        return browser
    
    def _add_performance_options(self, options: webdriver.ChromeOptions):
        """添加性能优化选项"""
        # 禁用图片加载（可选，取消注释以启用）
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # options.add_experimental_option("prefs", prefs)
        
        # 禁用 GPU 加速（在某些环境下可提高稳定性）
        options.add_argument('--disable-gpu')
        
        # 禁用扩展
        options.add_argument('--disable-extensions')
        
        # 禁用开发者共享内存
        options.add_argument('--disable-dev-shm-usage')
        
        # 禁用沙箱（在某些 Linux 环境下需要）
        options.add_argument('--no-sandbox')
        
        # 禁用信息栏
        options.add_argument('--disable-infobars')
        
        # 启用急切模式，加快页面加载
        options.page_load_strategy = 'eager'
        
        # 禁用后台网络服务
        options.add_argument('--disable-background-networking')
        
        # 禁用默认浏览器检查
        options.add_argument('--no-default-browser-check')
        
        # 禁用翻译服务
        options.add_argument('--disable-translate')
        
        # 禁用同步
        options.add_argument('--disable-sync')
    
    def _add_security_options(self, options: webdriver.ChromeOptions):
        """添加安全和证书相关选项"""
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-ssl-error')
        options.add_argument('--log-level=3')  # 减少日志输出
        
        # 允许运行不安全的内容
        options.add_argument('--allow-running-insecure-content')
    
    def _add_anti_detection_options(self, options: webdriver.ChromeOptions):
        """添加反自动化检测选项"""
        # 排除自动化控制提示
        options.add_experimental_option('excludeSwitches', [
            'enable-logging',
            'enable-automation'
        ])
        
        # 禁用自动化扩展
        options.add_experimental_option('useAutomationExtension', False)
        
        # 设置偏好
        prefs = {
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_setting_values.notifications': 2,  # 禁用通知
        }
        options.add_experimental_option('prefs', prefs)
    
    def _create_browser(self, config: Config, options: webdriver.ChromeOptions, 
                        log_path: str) -> webdriver.Chrome:
        """创建浏览器实例"""
        driver_path = config.get("browser", "driverPath", '') if config else ''
        
        try:
            if driver_path and os.path.exists(driver_path):
                # 使用指定的驱动路径
                service = ChromeService(executable_path=driver_path, log_path=log_path)
                logger.info(f"使用指定的 ChromeDriver: {driver_path}")
            else:
                # 自动下载和管理驱动
                service = ChromeService(
                    executable_path=ChromeDriverManager().install(),
                    log_path=log_path
                )
                logger.info("使用自动管理的 ChromeDriver")
            
            browser = webdriver.Chrome(service=service, options=options)
            logger.success("Chrome 浏览器初始化成功")
            return browser
            
        except Exception as e:
            logger.error(f"Chrome 浏览器初始化失败: {e}")
            raise
    
    def _execute_anti_detection_scripts(self, browser: webdriver.Chrome):
        """执行反检测 JavaScript 脚本"""
        try:
            # 隐藏 webdriver 属性
            browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // 修改 navigator.plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // 修改 navigator.languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en']
                    });
                    
                    // 隐藏自动化相关属性
                    window.chrome = {
                        runtime: {}
                    };
                '''
            })
            logger.debug("反检测脚本已注入")
        except Exception as e:
            logger.warning(f"反检测脚本注入失败: {e}")
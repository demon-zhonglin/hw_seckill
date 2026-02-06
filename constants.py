# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
常量定义模块
集中管理项目中使用的所有常量
"""

import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List


# ============================================================
# 项目路径定义
# ============================================================

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(PROJECT_PATH, "logs")
BASE_PROFILE_PATH = os.path.join(PROJECT_PATH, "profiles")
SELENIUM_LOG_FILE = os.path.join(LOG_PATH, "selenium.log")
COOKIES_FILE = os.path.join(PROJECT_PATH, "hw_cookies.txt")
CONFIG_FILE = os.path.join(PROJECT_PATH, "config.ini")


# ============================================================
# 华为官网页面 URL 定义
# ============================================================

class PageURL:
    """华为官网页面 URL"""
    INDEX = "www.vmall.com/index.html"
    LOGIN = "id1.cloud.huawei.com/CAS/portal/loginAuth.html"
    PRODUCT = "www.vmall.com/product/comdetail/index.html"
    ORDER = "www.vmall.com/order/nowConfirmcart"
    RUSH_ORDER = "www.vmall.com/order/rush/confirm"
    PAYMENT = "payment.vmall.com/cashier/web/pcIndex.htm"
    SERVER_TIME_API = "https://openapi.vmall.com/serverTime.json"


# 兼容旧代码
INDEX_PAGE_URL = PageURL.INDEX
LOGIN_PAGE_URL = PageURL.LOGIN
PRODUCT_PAGE_URL = PageURL.PRODUCT
ORDER_PAGE_URL = PageURL.ORDER
RUSH_ORDER_PAGE_URL = PageURL.RUSH_ORDER
PAYMENT_PAGE_URL = PageURL.PAYMENT


# ============================================================
# 页面信息定义
# ============================================================

@dataclass
class PageInfo:
    """页面信息"""
    page: str
    page_desc: str
    url: str


class Pages:
    """页面集合"""
    INDEX = PageInfo('index', '首页', PageURL.INDEX)
    LOGIN = PageInfo('login', '登录页', PageURL.LOGIN)
    PRODUCT = PageInfo('product', '产品页', PageURL.PRODUCT)
    ORDER = PageInfo('order', '下单页', PageURL.ORDER)
    RUSH_ORDER = PageInfo('rushorder', '抢购下单页', PageURL.RUSH_ORDER)
    PAYMENT = PageInfo('payment', '付款页', PageURL.PAYMENT)
    
    @classmethod
    def all(cls) -> List[Dict]:
        """获取所有页面信息（兼容旧代码）"""
        return [
            {'page': cls.INDEX.page, 'pageDesc': cls.INDEX.page_desc, 'url': cls.INDEX.url},
            {'page': cls.LOGIN.page, 'pageDesc': cls.LOGIN.page_desc, 'url': cls.LOGIN.url},
            {'page': cls.PRODUCT.page, 'pageDesc': cls.PRODUCT.page_desc, 'url': cls.PRODUCT.url},
            {'page': cls.ORDER.page, 'pageDesc': cls.ORDER.page_desc, 'url': cls.ORDER.url},
            {'page': cls.RUSH_ORDER.page, 'pageDesc': cls.RUSH_ORDER.page_desc, 'url': cls.RUSH_ORDER.url},
            {'page': cls.PAYMENT.page, 'pageDesc': cls.PAYMENT.page_desc, 'url': cls.PAYMENT.url},
        ]


# 兼容旧代码
PAGES = Pages.all()


# ============================================================
# 抢购状态枚举
# ============================================================

class BuyingStatus(Enum):
    """抢购状态"""
    WAITING = auto()          # 等待中
    COUNTDOWN = auto()        # 倒计时中
    BUYING = auto()           # 抢购中
    QUEUING = auto()          # 排队中
    SUBMITTING = auto()       # 提交订单中
    SUCCESS = auto()          # 抢购成功
    FAILED = auto()           # 抢购失败
    SOLD_OUT = auto()         # 已售罄


class LoginStatus(Enum):
    """登录状态"""
    NOT_LOGGED = auto()       # 未登录
    LOGGING = auto()          # 登录中
    NEED_CAPTCHA = auto()     # 需要验证码
    NEED_SMS = auto()         # 需要短信验证
    NEED_DEVICE = auto()      # 需要设备验证
    NEED_TRUST = auto()       # 需要信任浏览器
    LOGGED = auto()           # 已登录
    FAILED = auto()           # 登录失败


# ============================================================
# 提示文案定义
# ============================================================

class TipMessage:
    """提示消息"""
    SOLD_OUT = '抱歉，已售完，下次再来'
    NOT_GOT = '抱歉，没有抢到'
    NOT_GOT_2 = '抱歉，您没有抢到'
    ONLY_RESERVED = '抱歉，仅限预约用户购买'
    NOT_STARTED = '抢购活动未开始，看看其他商品吧'
    LIMIT_EXCEEDED = '本次发售商品数量有限，您已超过购买上限，将机会留给其他人吧'
    LIMIT_EXCEEDED_2 = '本次发售商品数量有限，您已超过购买上限，请勿重复购买，将机会留给其他人吧'
    ACTIVITY_ENDED = '活动已结束'
    NOT_QUALIFIED = '抱歉，不符合购买条件'
    NOT_QUALIFIED_2 = '抱歉，您不符合购买条件'
    REGISTER_QUEUE = '登记排队，有货时通知您'
    OUT_OF_STOCK = '抱歉，库存不足'
    LIMIT_REMAINING = '您已超过购买上限，本场活动最多还能买'
    QUEUE_TOO_MANY = '当前排队人数过多，是否继续排队等待？'
    QUEUING = '排队中'
    SECKILL_SOLD_OUT = '秒杀火爆<br/>该秒杀商品已售罄'


# 兼容旧代码
TIP_MSGS = [
    TipMessage.SOLD_OUT,
    TipMessage.NOT_GOT,
    TipMessage.NOT_GOT_2,
    TipMessage.ONLY_RESERVED,
    TipMessage.NOT_STARTED,
    TipMessage.LIMIT_EXCEEDED,
    TipMessage.LIMIT_EXCEEDED_2,
    TipMessage.ACTIVITY_ENDED,
    TipMessage.NOT_QUALIFIED,
    TipMessage.NOT_QUALIFIED_2,
    TipMessage.REGISTER_QUEUE,
    TipMessage.OUT_OF_STOCK,
    TipMessage.LIMIT_REMAINING,
    TipMessage.QUEUE_TOO_MANY,
    TipMessage.QUEUING,
    TipMessage.ACTIVITY_ENDED,
    TipMessage.SECKILL_SOLD_OUT,
]


# ============================================================
# CSS 选择器定义
# ============================================================

class Selectors:
    """页面元素选择器"""
    
    # 导航栏
    NAV_ELEMENT = "#navigationLayout > div > div:nth-child(3) > div > div > div:last-child"
    MENU_LINKS = 'div[data-testid="vui_popup_body_inner"] div[data-testid="vui_text_container"]'
    
    # 登录页面
    LOGIN_INPUT = ".hwid-input"
    LOGIN_BUTTON = ".hwid-login-btn"
    VERIFICATION_CODE_INPUT = ".hwid-dialog-main .hwid-getAuthCode-input .hwid-input-area .hwid-input"
    VERIFICATION_CODE_BTN = ".hwid-smsCode"
    DIALOG_SUBMIT_BTN = ".hwid-dialog-main .hwid-dialog-footer .hwid-button-base-box2 .dialogFooterBtn"
    TRUST_BROWSER = ".hwid-trustBrowser"
    TRUST_BROWSER_BTN = ".hwid-trustBrowser .hwid-dialog-textBtnBox .normalBtn"
    JIGSAW_MODAL = ".yidun_modal__wrap"
    DEVICE_CODE_INPUT = ".hwid-sixInputArea-line"
    
    # 产品页面
    BUY_BUTTON = "#prd-botnav-rightbtn"
    SKU_BUTTONS = ".css-175oi2r.r-1pkz85s.r-151r267.r-16pv4up.r-1keljc5.r-fg2qkj.r-187g3x.r-16qzwuk.r-1pb60y0.r-7898gx.r-m8azki.r-1o5risz.r-gu0qjt.r-9aemit.r-13qz1uu.r-1g40b8q .css-175oi2r.r-1loqt21.r-1otgn73"
    COUNTDOWN_ELEMENT = "#prd-detail .css-175oi2r.r-14lw9ot .css-175oi2r.r-14lw9ot.r-18u37iz.r-1wtj0ep .css-175oi2r.r-1wtj0ep .css-146c3p1.r-13uqrnb.r-oxtfae"
    
    # 弹窗
    BOX_CONTENT = "#show_risk_msg_box .box-ct .box-cc .box-content"
    BOX_OK_BTN = ".box-ct .box-cc .box-content .box-button .box-ok"
    IFRAME_BOX = "#iframeBox #queueIframe"
    RUSH_BUY_QUEUE = "#RushBuyQueue"
    QUEUE_TIPS = ".ecWeb-queue .queue-tips"
    QUEUE_BTN = ".ecWeb-queue .queue-btn .btn-ok"
    
    # 订单页面
    SUBMIT_ORDER_BTN = "#checkoutSubmit"
    AGREEMENT_CHECKBOX = "#agreementChecked"


# ============================================================
# 默认配置值
# ============================================================

class Defaults:
    """默认配置值"""
    THREAD_NUM = 1
    MAX_THREAD_NUM = 20
    BROWSER_TYPE = 'chrome'
    INTERVAL = 0.001
    MIN_INTERVAL = 0.001
    TIMEOUT = 30
    RETRY_TIMES = 3
    WAIT_TIMEOUT = 5
    WAIT_POLL_FREQUENCY = 0.01
    
    # 用户代理
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )


# 兼容旧代码
DEFAULT_THREAD_NUM = str(Defaults.THREAD_NUM)
DEFAULT_BROWSER_TYPE = Defaults.BROWSER_TYPE
RETRY_TIMES = Defaults.RETRY_TIMES


# ============================================================
# 支持的浏览器类型
# ============================================================

SUPPORTED_BROWSERS = ['chrome', 'firefox', 'edge', 'safari']


# ============================================================
# 版本信息
# ============================================================

VERSION = "2.0.0"
AUTHOR = "lov3smu"
PROJECT_NAME = "Hw_Seckill"
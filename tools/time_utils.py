# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
时间工具模块
提供服务器时间同步、倒计时计算等功能
"""

import math
import time
from datetime import datetime, timedelta
from typing import Tuple, List, Optional
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from loguru import logger


class TimeSync:
    """时间同步类，用于与华为服务器时间同步"""
    
    SERVER_TIME_URL = "https://openapi.vmall.com/serverTime.json"
    
    def __init__(self):
        self.session = self._create_session()
        self._server_timestamp: Optional[int] = None
        self._local_timestamp: Optional[int] = None
        self._time_diff: int = 0
        
    def _create_session(self) -> requests.Session:
        """创建带有重试机制的 Session"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置超时
        session.timeout = 5
        
        return session
    
    def sync(self) -> Tuple[int, int, int]:
        """
        同步华为服务器时间
        
        Returns:
            Tuple[server_timestamp, local_timestamp, diff_ms]
        """
        logger.info("开始同步华为服务器时间...")
        
        # 多次采样取平均值，提高精度
        samples = []
        for i in range(3):
            try:
                start_ts = self._local_time()
                server_ts = self._server_time()
                end_ts = self._local_time()
                
                if server_ts:
                    # 计算网络延迟的一半作为校正
                    latency = (end_ts - start_ts) / 2
                    local_ts = start_ts + latency
                    diff = local_ts - server_ts
                    samples.append((server_ts, local_ts, diff))
            except Exception as e:
                logger.warning(f"第{i+1}次时间同步失败: {e}")
                
            time.sleep(0.1)
        
        if not samples:
            logger.error("无法获取服务器时间，使用本地时间")
            local_ts = self._local_time()
            return local_ts, local_ts, 0
        
        # 取中位数，排除异常值
        samples.sort(key=lambda x: x[2])
        median_sample = samples[len(samples) // 2]
        
        self._server_timestamp = median_sample[0]
        self._local_timestamp = median_sample[1]
        self._time_diff = median_sample[2]
        
        logger.info(f"服务器时间: {self.timestamp_to_str(self._server_timestamp)}")
        logger.info(f"本地时间: {self.timestamp_to_str(self._local_timestamp)}")
        
        compare_result = "快于" if self._time_diff > 0 else "慢于"
        logger.info(f"本地时间{compare_result}服务器时间 {abs(self._time_diff)} 毫秒")
        
        return self._server_timestamp, self._local_timestamp, self._time_diff
    
    def _server_time(self) -> Optional[int]:
        """获取华为服务器时间戳（毫秒）"""
        try:
            response = self.session.get(self.SERVER_TIME_URL, timeout=3)
            if response.ok:
                data = response.json()
                return data.get('serverTimeMs')
        except Exception as e:
            logger.error(f"获取服务器时间失败: {e}")
        return None
    
    @staticmethod
    def _local_time() -> int:
        """获取本地时间戳（毫秒）"""
        return int(time.time() * 1000)
    
    @staticmethod
    def timestamp_to_str(timestamp: int) -> str:
        """将时间戳转换为可读字符串"""
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    @property
    def time_diff(self) -> int:
        """获取时间差（毫秒）"""
        return self._time_diff
    
    def get_server_time(self) -> int:
        """获取当前服务器时间（根据本地时间和时间差计算）"""
        return self._local_time() - self._time_diff


class CountdownTimer:
    """倒计时计时器"""
    
    def __init__(self, time_sync: TimeSync):
        self.time_sync = time_sync
        self._target_time: Optional[datetime] = None
        
    def set_target(self, target_time: datetime):
        """设置目标时间"""
        self._target_time = target_time
        logger.info(f"设置抢购目标时间: {target_time}")
    
    def get_remaining_ms(self) -> int:
        """获取剩余毫秒数"""
        if not self._target_time:
            return 0
        
        target_ts = int(self._target_time.timestamp() * 1000)
        current_server_ts = self.time_sync.get_server_time()
        return max(target_ts - current_server_ts, 0)
    
    def get_remaining_parts(self) -> Tuple[int, int, int, int, int]:
        """
        获取剩余时间各部分
        
        Returns:
            Tuple[days, hours, minutes, seconds, milliseconds]
        """
        remaining_ms = self.get_remaining_ms()
        
        days = remaining_ms // (24 * 60 * 60 * 1000)
        remaining_ms %= (24 * 60 * 60 * 1000)
        
        hours = remaining_ms // (60 * 60 * 1000)
        remaining_ms %= (60 * 60 * 1000)
        
        minutes = remaining_ms // (60 * 1000)
        remaining_ms %= (60 * 1000)
        
        seconds = remaining_ms // 1000
        milliseconds = remaining_ms % 1000
        
        return days, hours, minutes, seconds, milliseconds
    
    def format_remaining(self) -> str:
        """格式化剩余时间"""
        days, hours, minutes, seconds, ms = self.get_remaining_parts()
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0 or days > 0:
            parts.append(f"{hours:02d}时")
        parts.append(f"{minutes:02d}分")
        parts.append(f"{seconds:02d}秒")
        parts.append(f"{ms:03d}毫秒")
        
        return " ".join(parts)
    
    def is_time_to_start(self) -> bool:
        """是否到达开始时间"""
        return self.get_remaining_ms() <= 0
    
    def wait_until_ready(self, advance_ms: int = 100):
        """
        等待直到目标时间前 advance_ms 毫秒
        
        Args:
            advance_ms: 提前量（毫秒）
        """
        while True:
            remaining = self.get_remaining_ms()
            
            if remaining <= advance_ms:
                break
            elif remaining > 60000:  # > 1分钟
                logger.info(f"距离抢购开始: {self.format_remaining()}")
                time.sleep(10)
            elif remaining > 10000:  # > 10秒
                logger.info(f"距离抢购开始: {self.format_remaining()}")
                time.sleep(1)
            elif remaining > 1000:  # > 1秒
                logger.info(f"距离抢购开始: {self.format_remaining()}")
                time.sleep(0.1)
            else:
                time.sleep(0.001)


# 兼容旧接口的函数
def server_time() -> Optional[int]:
    """获取华为服务器时间"""
    logger.info("开始获取华为服务器时间")
    url = "https://openapi.vmall.com/serverTime.json"
    try:
        response = requests.get(url, timeout=5)
        if response.ok:
            data = response.json()
            return data['serverTimeMs']
    except Exception as e:
        logger.error(f"华为服务器获取时间失败: {e}")
    return None


def local_time() -> int:
    """获取本地机器时间"""
    logger.info("开始获取本地机器时间")
    return int(time.time() * 1000)


def local_hw_time_diff() -> Tuple[int, int, int]:
    """获取本地与华为服务器的时间差"""
    time_sync = TimeSync()
    return time_sync.sync()


def format_countdown_time(countdown_times: List[str]) -> str:
    """格式化倒计时"""
    countdown_time_units = ["天", "时", "分", "秒", "毫秒"]
    parts = []
    for i, t in enumerate(countdown_times):
        parts.append(f"{t}{countdown_time_units[i]}")
    return " ".join(parts)


def get_start_buying_time(countdown_times: List[str]) -> datetime:
    """根据倒计时计算开始时间"""
    current_date = datetime.now()
    days_delta = timedelta(days=int(countdown_times[0]))
    hours_delta = timedelta(hours=int(countdown_times[1]))
    minutes_delta = timedelta(minutes=int(countdown_times[2]))
    seconds_delta = timedelta(seconds=int(countdown_times[3]))
    return current_date + days_delta + hours_delta + minutes_delta + seconds_delta


def date_second_add(date: datetime, seconds: int) -> datetime:
    """日期加秒数"""
    return date + timedelta(seconds=seconds)


def milliseconds_diff(local_timestamp: int, hw_server_timestamp: int) -> int:
    """计算毫秒差"""
    return local_timestamp - hw_server_timestamp


def seconds_diff(d1: datetime, d2: datetime) -> float:
    """计算秒数差"""
    return (d2 - d1).total_seconds()


def timestamp2time(timestamp: int) -> str:
    """时间戳转字符串"""
    dt = datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def calc_countdown_ms_diff(target_date_time: datetime, ms_diff: int) -> int:
    """计算距离目标时间的毫秒差"""
    local_timestamp = local_time() - ms_diff
    target_timestamp = int(target_date_time.timestamp() * 1000)
    return target_timestamp - local_timestamp


def calc_countdown_times(target_date_time: datetime, ms_diff: int) -> List[str]:
    """计算倒计时各部分"""
    local_timestamp = local_time() - ms_diff
    target_timestamp = int(target_date_time.timestamp() * 1000)
    origin_timestamp_sec_diff = (target_timestamp - local_timestamp) / 1000
    timestamp_sec_diff = int(origin_timestamp_sec_diff)
    
    days = max(timestamp_sec_diff // 86400, 0)
    timestamp_sec_diff = timestamp_sec_diff - days * 86400
    hours = max(timestamp_sec_diff // 3600, 0)
    timestamp_sec_diff = timestamp_sec_diff - hours * 3600
    minutes = max(timestamp_sec_diff // 60, 0)
    seconds = max(timestamp_sec_diff - minutes * 60, 0)
    microseconds = max(
        int((origin_timestamp_sec_diff - days * 86400 - hours * 3600 - minutes * 60 - seconds) * 1000),
        0
    )
    
    return [
        str(days).zfill(2),
        str(hours).zfill(2),
        str(minutes).zfill(2),
        str(seconds).zfill(2),
        str(microseconds).zfill(3)
    ]
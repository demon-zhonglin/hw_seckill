# Hw_Seckill v2.0

华为商城自动抢购脚本，支持华为 Mate 系列手机及其他热门商品。

> ⚠️ 请确保 Python 版本 >= 3.8

## ✨ v2.0 更新内容

- 🎨 **全新界面**：彩色日志输出、美化的配置显示、进度条支持
- 🚀 **性能优化**：更快的时间同步、连接池复用、更精准的倒计时
- 🛡️ **稳定性增强**：完善的异常处理、自动重试机制、更好的错误提示
- 🔧 **功能增强**：
  - 命令行参数支持
  - 配置文件验证
  - 代理服务器支持
  - 抢购成功提示音
  - 邮件通知功能
  - 抢购统计信息
- 📦 **代码重构**：更清晰的模块划分、完善的类型注解、详细的文档注释

## 📋 特别声明

* 本仓库发布的 `hw_seckill` 项目仅用于**测试和学习研究**，禁止用于商业用途
* 本项目内所有资源文件，禁止任何公众号、自媒体进行任何形式的转载、发布
* 请勿将本项目用于商业或非法目的，否则后果自负
* 使用本项目即视为已接受此声明
* 本项目遵循 `GPL-3.0 License` 协议

## 🎯 主要功能

- [x] 自动登录华为商城（支持验证码、设备验证、信任浏览器）
- [x] 自动选择商品规格（颜色、版本、套装）
- [x] 精准时间同步（与华为服务器时间同步）
- [x] 自动抢购下单
- [x] 多线程并发抢购
- [x] 多浏览器支持（Chrome、Edge、Firefox）
- [x] 无头模式支持
- [x] 代理服务器支持
- [x] 抢购成功通知（声音、邮件）

## 🖥️ 运行环境

- Python >= 3.8
- Chrome / Edge / Firefox 浏览器
- 对应版本的浏览器驱动（支持自动下载）

### 浏览器驱动下载

| 浏览器 | 驱动下载地址 |
|--------|-------------|
| Chrome | [ChromeDriver](https://sites.google.com/chromium.org/driver/downloads) |
| Edge | [EdgeDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/) |
| Firefox | [GeckoDriver](https://github.com/mozilla/geckodriver/releases) |

> 💡 v2.0 版本支持自动下载驱动，无需手动配置

## 📦 安装依赖

```bash
# 使用清华镜像加速
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## ⚙️ 配置说明

编辑 `config.ini` 文件：

```ini
[user]
name=您的华为账号
password=您的密码

[product]
name=HUAWEI Mate XTs        # 商品名称（仅显示用）
id=10086754422315           # 商品ID（必填）
color=皓白                  # 商品颜色
version=16GB+1TB            # 商品版本
payment=全款购买            # 支付方式
sets=                       # 套装规格（留空则抢购单品）

[browser]
type=chrome                 # 浏览器类型
headless=no                 # 是否无头模式
; proxy=127.0.0.1:7890      # 代理服务器（可选）

[process]
thread=1                    # 并发线程数（1-20）
interval=0.001              # 下单间隔（秒）
timeout=30                  # 操作超时时间
retryTimes=3                # 失败重试次数

[notify]
enableSound=yes             # 成功提示音
enableEmail=no              # 邮件通知
```

### 获取商品 ID

1. 打开华为商城商品页面
2. URL 中的 `prdId` 参数即为商品 ID
3. 例如：`https://www.vmall.com/product/comdetail/index.html?prdId=10086754422315`

## 🚀 使用方法

### 基本使用

```bash
python main.py
```

### 命令行参数

```bash
# 查看帮助
python main.py -h

# 指定配置文件
python main.py -c /path/to/config.ini

# 开启调试模式
python main.py -d

# 仅验证配置文件
python main.py --validate

# 查看版本
python main.py -v
```

### 定时运行

**Windows (wait_to_run.bat)**:
```batch
@echo off
echo 等待抢购时间...
timeout /t 60
python main.py
```

**Linux/macOS (wait_to_run.sh)**:
```bash
#!/bin/bash
echo "等待抢购时间..."
sleep 60
python3 main.py
```

## 📊 项目结构

```
hw_seckill/
├── main.py              # 程序入口
├── huawei.py            # 核心业务逻辑
├── huawei_thread.py     # 多线程支持
├── config.py            # 配置管理
├── config.ini           # 配置文件
├── constants.py         # 常量定义
├── browser/             # 浏览器驱动模块
│   ├── browser_factory.py
│   ├── chrome.py
│   ├── edge.py
│   └── firefox.py
├── tools/               # 工具模块
│   ├── time_utils.py    # 时间工具
│   ├── utils.py         # 通用工具
│   └── my_logger.py     # 日志配置
├── logs/                # 日志目录
├── profiles/            # 浏览器配置目录
└── requirements.txt     # 依赖列表
```

## 🔧 常见问题

### 1. 浏览器驱动版本不匹配

程序会自动下载匹配的驱动，如遇问题请手动下载对应版本驱动，并在配置中指定路径。

### 2. 登录验证问题

- 首次登录需要手动完成拼图验证
- 短信验证码会自动发送，需要手动输入
- 建议提前登录一次，信任浏览器

### 3. 抢购失败

- 检查网络连接
- 确保商品 ID 正确
- 增加线程数
- 使用代理服务器

### 4. 无头模式问题

使用无头模式时，请务必配置 `userAgent`，否则可能被识别为自动化程序。

## 📝 更新日志

### v2.0.0 (2026-02-06)
由Ai优化
- 全面重构代码
- 添加配置验证功能
- 添加代理支持
- 添加邮件通知
- 优化时间同步精度
- 美化界面输出

### v1.0.0
- 原作者版本

## 🙏 致谢

致谢原作者以及所有贡献者和使用者的支持！

## 📄 License

[GPL-3.0 License](LICENSE)

# ETH Perp Core

实时监控 OKX ETH 永续合约行情，计算技术 + 资金因子并推送 QQ 邮箱的信号引擎（演示版，无自动交易）。

## 目录结构
```
eth_perp_core/
  config/config.yaml              # 参数
  adapters/                       # 数据接入
  core/                           # 基础组件
  indicators/                     # 指标与因子压缩
  fusion/                         # 融合与信号
  report/                         # 报告生成
  notifier/                       # 邮件推送
  tests/                          # 单元测试
  main.py                         # 入口
```

## 安装与运行
1. 安装依赖
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

2. 配置 QQ SMTP 授权码
```bash
export QQ_SMTP_AUTH="你的QQ邮箱SMTP授权码"
```

3. 调整 `config/config.yaml`
- `sender_email` / `receiver_emails`
- `heartbeat_interval_sec` 为 0 关闭心跳

4. 运行（仅演示，需外网）
```bash
python main.py
```

## 核心流程
- 启动先通过 REST warm-up 拉取 1m/5m/30m 历史 K 线
- WS 订阅 1 分钟收盘（confirm=1）后：
  - 计算 RSI / MACD / BOLL / EMA 斜率 / CCI / ATR
  - 压缩出 Trend / Momentum / Volatility 三因子
  - 定时 REST 拉 OI + Funding 压缩 LeverageFlow
  - 按权重融合得到 FinalFactor，动态阈值 = k * Volatility
  - confirm_n 连续满足 + cooldown_n 冷却后给出 LONG/SHORT/NEUTRAL
  - 信号变化或心跳触发 QQ 邮件推送

## 输出示例
```
## ETH-USDT-SWAP Signal
- Time: 2024-01-01T00:00:00+00:00
- Signal: **LONG**
- FinalFactor: 0.4123
- Threshold: 0.1200
### Factor Contribution
- Trend: 0.1800
- Momentum: 0.0400
- Volatility: 0.0120
- LeverageFlow: 0.1803
### Key Indicators
- rsi: 55.12
- macd_hist: 0.0031
- cci: 25.0
- atr: 8.2
### Derivatives
- OI: 123456.0
- Funding: 0.0001
```

## 测试
```bash
pytest -q
```

## 风险提示
- 本项目仅为信号演示，不构成投资建议；请谨慎使用，风险自负。
- 外部接口依赖网络与交易所可用性，实际运行需处理断线与限频。

# Eindhoven 预约监控工具

这是一个用于监控 Eindhoven 预约系统空位的自动化工具。

## 功能特性

- 🔍 **自动监控**：定期检查预约系统的可用空位
- 📱 **智能推送**：通过 PushPlus 发送通知消息
- ⏰ **时间记录**：记录并比较最早可预约时间
- 🚀 **优化通知**：只有发现更早时间或首次发现时才推送通知

## 主要功能

1. **自动查询**：每2分钟查询一次预约系统
2. **智能判断**：
   - 首次发现空位时立即通知
   - 发现更早时间时推送两条消息（强调更早时间 + 正常通知）
   - 相同时间只在首次发现时通知
   - 更晚时间不通知
3. **持久化存储**：将最早时间保存到文件中，程序重启后继续使用

## 文件说明

- `main.py`：主程序文件
- `pushplus.py`：PushPlus推送模块
- `config.py`：配置文件（包含敏感信息，不会被推送）
- `config.example.py`：示例配置文件
- `earliest_time.txt`：记录的最早可预约时间（自动生成）
- `.gitignore`：Git忽略文件配置

## 使用方法

1. 安装依赖：
```bash
pip install requests
```

2. 配置PushPlus Token：
   - 复制 `config.example.py` 为 `config.py`
   - 在 `config.py` 中修改 `PUSHPLUS_TOKEN` 为你的PushPlus Token
   - 根据需要调整 `INTERVAL` 查询间隔时间

3. 运行程序：
```bash
python main.py
```

## 配置说明

- `INTERVAL`：查询间隔时间（秒），默认120秒
- `PUSHPLUS_TOKEN`：PushPlus推送服务的Token
- `headers`：HTTP请求头，包含认证信息

## 推送消息格式

- **首次发现**：`有空位 - 2025-08-18 10:40`
- **发现更早时间**：
  - `发现更早时间！- 2025-08-18 10:40`
  - `有空位 - 2025-08-18 10:40`

## 注意事项

- 程序会持续运行，按Ctrl+C停止
- 最早时间记录保存在 `earliest_time.txt` 文件中
- 确保网络连接正常以访问预约系统 
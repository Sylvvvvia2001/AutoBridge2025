# 在Cursor中调试ESP8266温湿度监测系统

本指南将帮助你在Cursor中调试ESP8266温湿度监测系统的Python模拟器代码。

## 文件说明

本项目包含以下Python文件，按照复杂度递增排序：

1. `dht11_ha_api.py` - 命令行版本，使用简单的HTTP请求与Home Assistant通信
2. `ha_python_client.py` - 使用官方Home Assistant Python库的版本
3. `dht11_ha_simulator.py` - 带有GUI界面的图形模拟器版本

## 在Cursor中调试步骤

### 准备工作

1. 确保Cursor环境中已安装Python 3.6+
2. 根据需要安装依赖库：

```bash
# 对于dht11_ha_api.py
pip install requests

# 对于ha_python_client.py
pip install homeassistant-api

# 对于dht11_ha_simulator.py
pip install pillow tkinter
```

### 调试基本HTTP版本 (dht11_ha_api.py)

1. 打开`dht11_ha_api.py`文件
2. 修改配置部分，特别是：
   - `HA_HOST` - 你的Home Assistant IP地址
   - `HA_PORT` - 通常是8123
   - `HA_TOKEN` - 从Home Assistant获取的长期访问令牌
   - `SEND_INTERVAL` - 可以设置较小值方便测试，如10秒
   - `DEBUG_MODE` - 设置为`True`进行调试模式，不会实际发送数据

3. 设置调试断点：
   - 在读取传感器数据的行
   - 在发送数据到Home Assistant之前
   - 在错误处理部分

4. 在Cursor中运行代码：
   ```
   python dht11_ha_api.py
   ```

### 调试官方API版本 (ha_python_client.py)

1. 确保已安装homeassistant-api库：
   ```
   pip install homeassistant-api
   ```

2. 打开`ha_python_client.py`文件
3. 修改配置部分，特别是：
   - `HA_URL` - 你的Home Assistant完整URL，如`http://192.168.1.100:8123`
   - `HA_TOKEN` - 从Home Assistant获取的长期访问令牌

4. 设置调试断点
5. 在Cursor中运行代码：
   ```
   python ha_python_client.py
   ```

### 调试GUI模拟器版本 (dht11_ha_simulator.py)

这个版本在Cursor中可能无法完全运行GUI界面，但你仍然可以调试代码逻辑：

1. 确保已安装tkinter和pillow库
2. 打开`dht11_ha_simulator.py`文件
3. 设置断点在传感器数据生成和发送数据部分
4. 在Cursor中运行代码：
   ```
   python dht11_ha_simulator.py
   ```

## 调试技巧

1. **使用print调试**：
   - 添加print语句输出变量值
   - 使用`logging`模块代替print，已配置在代码中

2. **修改调试模式**：
   - 所有脚本都包含`DEBUG_MODE`变量
   - 设置为`True`时，只会打印而不会实际发送数据到Home Assistant

3. **减少发送间隔**：
   - 设置`SEND_INTERVAL`为较小值，如10秒，方便测试

4. **模拟数据调整**：
   - 修改`BASE_TEMPERATURE`和`BASE_HUMIDITY`值进行不同场景测试
   - 调整`VARIATION`值改变随机波动范围

## 连接到实际ESP8266

如果你想在调试完成后将代码部署到实际ESP8266设备上，可以参考以下步骤：

1. 安装Arduino IDE并添加ESP8266支持
2. 打开`dht11_esp8266.ino`文件
3. 将调试通过的配置值更新到Arduino代码中
4. 通过USB连接ESP8266，上传代码

## 排查常见问题

1. **连接失败问题**：
   - 检查Home Assistant URL/IP是否正确
   - 验证长期访问令牌是否有效
   - 确保网络连接正常

2. **导入错误**：
   - 确保所有依赖库已正确安装

3. **数据不显示在Home Assistant**：
   - 检查实体ID是否正确
   - 验证API请求是否成功
   - 查看Home Assistant日志中的错误

4. **Cursor中GUI不显示**：
   - 这是正常的，GUI应用可能需要本地Python环境运行

---

通过这些Python模拟器，你可以在不需要物理硬件的情况下开发和测试Home Assistant的集成功能，为后续部署到实际ESP8266设备做好准备。 
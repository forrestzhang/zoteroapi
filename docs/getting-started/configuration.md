# Zotero 本地服务器配置

在使用 ZoteroAPI 之前，你需要在 Zotero 桌面应用中启用本地服务器功能。本页面将指导你完成配置过程。

## 前置条件

确保你已经：

- ✅ 安装了 Zotero 桌面应用程序（[下载地址](https://www.zotero.org/download/)）
- ✅ 安装了 ZoteroAPI Python 库（参见 [安装指南](installation.md)）

## 启用本地服务器

### 第一步：打开 Zotero 设置

1. 启动 Zotero 桌面应用
2. 进入设置界面：
   - **Windows/Linux**：编辑 → 首选项
   - **macOS**：Zotero → 偏好设置

### 第二步：启用 HTTP 服务器

1. 在设置窗口中，选择 **高级** 标签页
2. 点击 **文件和文件夹** 子标签
3. 找到 **允许其他应用程序访问 Zotero** 相关选项

!!! warning "注意"
    不同版本的 Zotero 界面可能略有差异，但核心设置项是一致的。

### 第三步：配置网络访问

在高级设置中：

1. 勾选 **允许其他应用程序访问 Zotero**
2. 默认端口通常为 `23119`（一般不需要修改）

![Zotero 设置界面](../assets/images/zotero_settings.png)

!!! tip "端口说明"
    如果默认端口被占用，你可以修改为其他端口（如 `23120`），但需要在初始化 ZoteroAPI 客户端时指定对应的端口。

### 第四步：验证服务器状态

配置完成后，Zotero 会在后台启动本地 HTTP 服务器。你可以通过以下方式验证：

#### 方法 1：浏览器验证

在浏览器中访问：

```
http://localhost:23119/
```

如果看到类似 "Zotero API" 或相关信息，说明服务器已成功启动。

#### 方法 2：Python 验证

运行以下 Python 代码：

```python
from zoteroapi import ZoteroLocal

try:
    client = ZoteroLocal()
    items = client.get_items_top(limit=1)
    print("✅ 连接成功！")
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

## 自定义配置

### 修改默认端口

如果你修改了 Zotero 的默认端口，需要在初始化客户端时指定：

```python
from zoteroapi import ZoteroLocal

# 使用自定义端口
client = ZoteroLocal(base_url="http://localhost:23120")
```

### 远程访问配置

!!! danger "安全警告"
    默认情况下，Zotero 本地服务器只允许本地访问（localhost）。如果需要远程访问，请务必了解相关安全风险。

如果需要从其他机器访问 Zotero 服务器：

1. 在 Zotero 设置中配置允许的 IP 地址
2. 确保防火墙允许对应端口的访问
3. 在 ZoteroAPI 中指定远程地址：

```python
client = ZoteroLocal(base_url="http://192.168.1.100:23119")
```

## 常见问题

### 无法连接到本地服务器

!!! error "错误信息"
    `ConnectionError: Failed to connect to Zotero local server`

**可能原因和解决方案**：

1. **Zotero 未启动**
   - 确保 Zotero 桌面应用正在运行

2. **未启用本地服务器**
   - 检查设置中是否勾选了"允许其他应用程序访问 Zotero"

3. **端口被占用或修改**
   - 检查 Zotero 设置中的端口号
   - 在代码中使用正确的端口号

4. **防火墙阻止**
   - 检查防火墙设置，允许 Zotero 的网络访问

### 权限错误

!!! error "错误信息"
    `AuthenticationError: Access denied`

**解决方案**：

- 检查 Zotero 的访问权限设置
- 确认没有设置访问密码或 API 密钥限制

### 服务器响应慢

如果本地服务器响应缓慢：

1. **检查 Zotero 数据库大小**
   - 大型文献库可能导致响应变慢
   - 考虑优化数据库或使用 `limit` 参数限制返回数据量

2. **增加超时时间**（如需要）：

```python
# 注意：当前版本未提供超时配置，这是未来可能的扩展
# client = ZoteroLocal(timeout=30)
```

### macOS 安全提示

在 macOS 上，系统可能会提示网络访问权限：

1. 点击"允许"授予 Zotero 网络访问权限
2. 如果不小心拒绝了，可以在"系统偏好设置 → 安全性与隐私 → 防火墙 → 防火墙选项"中修改

## 配置检查清单

在继续使用 ZoteroAPI 之前，请确认：

- [ ] Zotero 桌面应用已安装并运行
- [ ] 已在 Zotero 设置中启用"允许其他应用程序访问"
- [ ] 能够通过浏览器访问 `http://localhost:23119/`
- [ ] Python 代码能成功连接到本地服务器

## 下一步

配置完成后，你可以开始使用 ZoteroAPI：

- [:material-arrow-right: 快速上手教程](quick-start.md)
- [:material-arrow-right: 客户端初始化详解](../user-guide/client-initialization.md)

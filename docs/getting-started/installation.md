# 安装指南

本页面将指导你完成 ZoteroAPI 的安装过程。

## 系统要求

在开始之前，请确保你的系统满足以下要求：

- **Python 版本**：Python 3.11 或更高版本
- **操作系统**：Windows、macOS 或 Linux
- **Zotero**：已安装 Zotero 桌面应用程序

!!! tip "检查 Python 版本"
    在终端中运行以下命令检查你的 Python 版本：
    ```bash
    python --version
    # 或
    python3 --version
    ```

## 使用 pip 安装（推荐）

这是最简单和推荐的安装方式：

```bash
pip install zoteroapi
```

!!! note "使用虚拟环境"
    我们强烈建议在虚拟环境中安装 ZoteroAPI，以避免依赖冲突：
    
    ```bash
    # 创建虚拟环境
    python -m venv .venv
    
    # 激活虚拟环境
    # Windows:
    .venv\Scripts\activate
    
    # macOS/Linux:
    source .venv/bin/activate
    
    # 安装 ZoteroAPI
    pip install zoteroapi
    ```

## 从源码安装

如果你需要最新的开发版本或想要修改源代码，可以从 GitHub 克隆仓库：

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/zoteroapi.git
cd zoteroapi
```

### 2. 安装依赖

```bash
# 安装基础依赖
pip install -e .

# 或安装包含开发工具的完整依赖
pip install -e ".[test,docs]"
```

!!! info "可选依赖说明"
    - `test`：包含测试相关依赖（pytest、pytest-cov 等）
    - `docs`：包含文档构建依赖（mkdocs、mkdocs-material 等）

## 验证安装

安装完成后，你可以通过以下方式验证安装是否成功：

### 方法 1：检查包版本

```bash
pip show zoteroapi
```

你应该看到类似以下的输出：

```
Name: zoteroapi
Version: 0.1.1
Summary: This is a Python client library for accessing the local Zotero server API.
...
```

### 方法 2：导入测试

在 Python 交互式环境中尝试导入：

```python
>>> from zoteroapi import ZoteroLocal
>>> print(ZoteroLocal.__doc__)
```

如果没有报错，说明安装成功！

## 依赖项

ZoteroAPI 只有一个核心依赖：

| 依赖包 | 版本要求 | 用途 |
|--------|----------|------|
| requests | >= 2.25.0 | HTTP 请求库，用于与 Zotero 本地服务器通信 |

所有依赖会在安装时自动安装。

## 升级 ZoteroAPI

要升级到最新版本，运行：

```bash
pip install --upgrade zoteroapi
```

## 卸载

如果需要卸载 ZoteroAPI：

```bash
pip uninstall zoteroapi
```

## 常见问题

### Python 版本过低

!!! error "错误信息"
    `ERROR: Package 'zoteroapi' requires a different Python: 3.9.0 not in '>=3.11'`

**解决方案**：升级到 Python 3.11 或更高版本。你可以从 [Python 官网](https://www.python.org/downloads/)下载最新版本。

### 网络问题导致安装失败

如果由于网络问题无法从 PyPI 安装，可以尝试使用国内镜像：

```bash
# 使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple zoteroapi

# 使用阿里云镜像
pip install -i https://mirrors.aliyun.com/pypi/simple/ zoteroapi
```

### 权限错误

!!! error "错误信息"
    `ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied`

**解决方案**：使用用户模式安装（不推荐）或使用虚拟环境（推荐）：

```bash
# 用户模式安装
pip install --user zoteroapi

# 或创建虚拟环境（推荐）
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install zoteroapi
```

## 下一步

安装完成后，你需要配置 Zotero 本地服务器：

- [:material-arrow-right: 配置 Zotero 本地服务器](configuration.md)
- [:material-arrow-right: 5 分钟快速上手](quick-start.md)

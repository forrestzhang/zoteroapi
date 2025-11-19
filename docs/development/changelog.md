# 更新日志

本文档记录了 ZoteroAPI 项目的所有重要变更。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)。

## [未发布]

### 新增
- 为所有 API 方法添加了完整的类型提示
- 改进了错误处理机制，支持更详细的错误信息
- 添加了性能监控和指标收集功能
- 新增了插件系统支持
- 添加了异步客户端支持（实验性）

### 改进
- 优化了 HTTP 连接池配置，提高了并发性能
- 改进了缓存机制，支持更灵活的缓存策略
- 增强了搜索功能，支持更复杂的搜索条件
- 优化了文件下载的内存使用
- 改进了文档生成和部署流程

### 修复
- 修复了处理压缩文件时的内存泄漏问题
- 修复了在某些情况下 URL 路径处理不正确的问题
- 修复了搜索功能中的大小写敏感性问题
- 修复了异常链断裂导致调试困难的问题

### 安全
- 改进了文件路径验证，防止路径遍历攻击
- 添加了请求超时配置，防止长时间挂起

## [0.1.1] - 2024-01-15

### 新增
- 添加了 `get_pmid()` 方法用于获取文献的 PMID
- 添加了 `copy_attachment_to_downloads()` 方法用于复制附件到下载目录
- 新增了完整的开发者文档和 API 参考
- 添加了代码覆盖率报告，当前覆盖率达到 88.14%

### 改进
- 改进了 `get_item_attachment_href()` 方法的错误处理
- 优化了文件上传的性能和稳定性
- 增强了异常信息的可读性和调试友好性
- 改进了 Mixin 类的文档字符串和类型注解

### 修复
- 修复了 `FilesMixin._normalize_path()` 方法在 Windows 系统上的路径处理问题
- 修复了 `search_by_title()` 方法在精确匹配模式下的逻辑错误
- 修复了处理没有附件的文献时的异常处理问题

## [0.1.0] - 2024-01-01

### 新增
- 🎉 首次发布 ZoteroAPI v0.1.0
- 实现了与 Zotero 本地服务器的基础 API 交互
- 支持文献条目的 CRUD 操作
- 实现了搜索功能（关键词、DOI、PMID、标题）
- 添加了文件下载和上传功能
- 支持笔记的创建和管理
- 提供了完整的异常处理体系

### 核心功能
- **文献管理**: `get_item()`, `get_items()`, `get_items_top()`
- **文献集操作**: `get_collections()`, `get_collection()`, `get_collection_items()`
- **搜索功能**: `search_items()`, `search_by_doi()`, `search_by_pmid()`, `search_by_title()`
- **文件操作**: `get_item_file()`, `download_file()`, `upload_file()`
- **笔记管理**: `get_note()`, `get_item_notes()`, `add_item_note()`
- **标签管理**: `get_tags()`

### 架构特性
- 采用 Mixin 模式实现功能模块化
- 使用 `requests.Session` 实现连接复用
- 提供完整的异常层次结构
- 支持跨平台路径处理
- 自动处理文件压缩和解压缩

### 文档
- 完整的 README.md 文档
- 详细的 API 参考文档
- 丰富的使用示例
- 开发者指南和贡献指南

### 测试
- 111 个测试用例，100% 通过率
- 88.14% 的代码覆盖率
- 包含单元测试和集成测试
- 使用 pytest 框架和 fixtures

### 平台支持
- Python 3.11+
- Windows, macOS, Linux
- 支持 Zotero 6.0+

---

## 版本号说明

ZoteroAPI 使用 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 变更类型

- `新增` - 新功能
- `更改` - 对现有功能的变更
- `弃用` - 即将移除的功能
- `移除` - 已移除的功能
- `修复` - 问题修复
- `安全` - 安全相关的修复

## 贡献者

感谢所有为 ZoteroAPI 项目做出贡献的开发者：

- **Tao Zhang** - 项目创建者和主要维护者
- 所有提交 Issue 和 Pull Request 的社区成员

## 路线图

### 即将发布的功能

#### v0.2.0 (计划中)
- [ ] 异步 API 客户端
- [ ] 插件系统正式版
- [ ] 高级搜索功能（布尔搜索、字段搜索）
- [ ] 批量操作 API
- [ ] 数据导入/导出功能

#### v0.3.0 (计划中)
- [ ] Zotero Web API 支持
- [ ] 文献关系图谱
- [ ] 智能分类和标签建议
- [ ] 性能监控面板
- [ ] 缓存策略优化

#### v1.0.0 (长期目标)
- [ ] 稳定的 API 接口
- [ ] 完整的文档和教程
- [ ] 生产环境部署支持
- [ ] 社区插件生态系统
- [ ] 多语言支持

### 技术债务

- [ ] 完善错误恢复机制
- [ ] 优化大型文献库的性能
- [ ] 改进缓存策略
- [ ] 增强安全性验证
- [ ] 完善并发处理

## 发布说明

### 如何获取更新

```bash
# 从 PyPI 安装最新版本
pip install --upgrade zoteroapi

# 从 GitHub 安装开发版本
pip install git+https://github.com/yourusername/zoteroapi.git
```

### 兼容性说明

- **主版本升级**可能包含不兼容的变更，请仔细阅读发布说明
- **次版本升级**通常是向后兼容的，可以直接升级
- **修订版本升级**只包含 bug 修复，可以安全升级

### 迁移指南

当主版本升级时，我们将提供详细的迁移指南，帮助用户平滑升级。

## 反馈和支持

如果您在使用过程中遇到问题或有改进建议，请：

1. 查看 [文档](https://yourusername.github.io/zoteroapi/)
2. 搜索 [Issues](https://github.com/yourusername/zoteroapi/issues)
3. 创建新的 Issue 或加入 [Discussions](https://github.com/yourusername/zoteroapi/discussions)
4. 提交 Pull Request 贡献代码

---

感谢您使用 ZoteroAPI！您的反馈和贡献是我们持续改进的动力。
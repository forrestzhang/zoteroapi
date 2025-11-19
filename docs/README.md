# ZoteroAPI 文档

本目录包含 ZoteroAPI 项目的完整文档，使用 MkDocs 构建。

## 文档结构

```
docs/
├── index.md                    # 首页
├── getting-started/            # 快速开始
│   ├── installation.md         # 安装指南
│   ├── configuration.md        # Zotero 配置
│   └── quick-start.md          # 快速上手
├── user-guide/                 # 用户指南
│   ├── client-initialization.md
│   ├── items-management.md
│   ├── collections.md
│   ├── search.md
│   ├── notes.md
│   ├── files.md
│   └── tags.md
├── examples/                   # 示例代码
├── api-reference/              # API 参考（自动生成）
├── development/                # 开发指南
└── faq.md                      # 常见问题
```

## 本地预览文档

### 安装文档依赖

```bash
pip install -e ".[docs]"
```

### 启动本地服务器

```bash
mkdocs serve
```

然后在浏览器访问 `http://127.0.0.1:8000`

## 构建文档

生成静态 HTML 文件：

```bash
mkdocs build
```

生成的文件位于 `site/` 目录。

## 部署文档

### GitHub Pages

```bash
mkdocs gh-deploy
```

### 自定义部署

将 `site/` 目录的内容部署到任何静态网站托管服务。

## 文档编写指南

### 添加新页面

1. 在 `docs/` 目录创建 Markdown 文件
2. 在 `mkdocs.yml` 的 `nav` 部分添加导航项
3. 使用 `mkdocs serve` 预览效果

### Markdown 扩展

文档支持以下 Markdown 扩展：

- **代码高亮**：使用三重反引号标记代码块
- **警告框**：使用 `!!! note`、`!!! tip`、`!!! warning` 等
- **标签页**：使用 `=== "标题"` 语法
- **Mermaid 图表**：在代码块中使用 `mermaid` 语言标识

### API 文档自动生成

API 参考文档使用 mkdocstrings 自动从源代码生成。在 Markdown 中使用：

```markdown
::: zoteroapi.client.ZoteroLocal
    options:
      show_source: true
```

## 更新文档

修改文档后：

1. 本地测试：`mkdocs serve`
2. 构建验证：`mkdocs build`
3. 提交更改
4. 部署（如果需要）：`mkdocs gh-deploy`

## 相关资源

- [MkDocs 官方文档](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings 文档](https://mkdocstrings.github.io/)

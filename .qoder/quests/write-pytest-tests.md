# ZoteroAPI 项目 Pytest 测试方案设计

## 概述

为 ZoteroAPI 项目建立完整的 pytest 测试体系，覆盖所有核心功能模块，确保代码质量和稳定性。

## 测试范围与目标

### 核心测试目标

- 单元测试覆盖率达到 85% 以上
- 所有公开 API 方法均需测试
- 异常情况和边界条件处理验证
- Mixin 模块功能独立测试
- 集成测试验证完整工作流

### 测试范围

1. 基础客户端层（BaseZoteroClient）
2. 主客户端（ZoteroLocal）
3. 功能混入模块（SearchMixin、FilesMixin、NotesMixin）
4. 异常处理机制
5. 工具方法和辅助函数

## 测试环境配置

### 依赖管理

在 pyproject.toml 中新增测试依赖配置段：

| 依赖包 | 版本要求 | 用途 |
|--------|---------|------|
| pytest | >=7.0.0 | 测试框架核心 |
| pytest-cov | >=4.0.0 | 覆盖率报告 |
| pytest-mock | >=3.10.0 | Mock 功能增强 |
| requests-mock | >=1.9.0 | HTTP 请求模拟 |
| pytest-asyncio | latest | 异步测试支持（备用） |
| pytest-xdist | latest | 并行测试执行 |

### 测试配置文件

需要创建 pytest.ini 配置文件，包含以下配置项：

- 测试发现路径：tests 目录
- 测试文件命名模式：test_*.py 或 *_test.py
- 最小覆盖率要求：85%
- 覆盖率报告格式：terminal + HTML
- 测试输出详细程度：verbose
- 日志捕获级别：INFO
- 标记定义：unit、integration、slow

## 测试目录结构设计

```
tests/
├── conftest.py                    # pytest 全局配置和共享 fixtures
├── unit/                          # 单元测试目录
│   ├── test_base_client.py        # 基础客户端测试
│   ├── test_client.py             # 主客户端测试
│   ├── test_exceptions.py         # 异常类测试
│   └── mixins/                    # Mixin 模块测试
│       ├── test_search.py         # 搜索功能测试
│       ├── test_files.py          # 文件操作测试
│       └── test_notes.py          # 笔记功能测试
├── integration/                   # 集成测试目录
│   ├── test_workflows.py          # 完整工作流测试
│   └── test_api_integration.py    # API 集成测试
├── fixtures/                      # 测试数据目录
│   ├── sample_responses.py        # 模拟 API 响应数据
│   ├── test_files/                # 测试用文件
│   └── mock_data.py               # Mock 数据工厂
└── utils/                         # 测试工具
    ├── helpers.py                 # 测试辅助函数
    └── assertions.py              # 自定义断言
```

## 共享 Fixtures 设计

### conftest.py 核心 Fixtures

| Fixture 名称 | 作用域 | 说明 |
|-------------|--------|------|
| mock_client | function | 返回配置好的 Mock ZoteroLocal 客户端实例 |
| base_client | function | 返回 BaseZoteroClient 实例 |
| mock_requests | function | 提供 requests-mock mocker 对象 |
| sample_item_data | session | 提供样本条目数据字典 |
| sample_collection_data | session | 提供样本文献集数据 |
| sample_note_data | session | 提供样本笔记数据 |
| temp_test_file | function | 创建临时测试文件，测试后自动清理 |
| temp_download_dir | function | 创建临时下载目录，测试后自动清理 |
| mock_api_responses | session | 预定义的 API 响应数据集合 |

### Fixture 实现要点

1. 使用 pytest.fixture 装饰器定义
2. 合理设置作用域（function/session）避免测试污染
3. 使用 yield 实现资源清理（teardown）
4. 提供参数化支持以适应不同测试场景

## 单元测试设计

### BaseZoteroClient 测试（test_base_client.py）

#### 测试用例列表

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_client_init_default | 默认初始化 | 验证默认 base_url 正确设置 |
| test_client_init_custom_url | 自定义 URL 初始化 | URL 格式化和 trailing slash 处理 |
| test_make_request_success | 成功的 API 请求 | 请求参数正确传递，响应正常返回 |
| test_make_request_with_params | 带查询参数请求 | params 正确拼接到 URL |
| test_make_request_auto_format | 自动添加 format 参数 | 未指定时默认添加 format=json |
| test_make_request_http_error | HTTP 错误处理 | 捕获并抛出 ZoteroLocalError |
| test_make_request_network_error | 网络错误处理 | RequestException 转换为 ZoteroLocalError |
| test_request_method_raw_response | 原始响应返回 | raw_response=True 时返回 Response 对象 |
| test_request_method_404_error | 404 错误处理 | 抛出 ResourceNotFound 异常 |
| test_session_persistence | Session 复用 | 验证 _session 对象在多次请求中复用 |

#### Mock 策略

- 使用 requests_mock 模拟所有 HTTP 请求
- 预设不同 HTTP 状态码的响应场景
- 验证请求 URL、方法、参数的准确性

### ZoteroLocal 主客户端测试（test_client.py）

#### 条目操作测试

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_get_item | 获取单个条目 | 返回正确的条目数据结构 |
| test_get_item_not_found | 条目不存在 | 抛出适当异常 |
| test_get_items | 获取所有条目 | 返回条目列表 |
| test_get_items_with_limit | 带限制参数获取 | limit 参数正确传递 |
| test_get_items_top | 获取顶层条目 | 正确过滤顶层条目 |
| test_get_item_by_key | 通过 key 获取条目 | 与 get_item 行为一致性 |

#### 文献集操作测试

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_get_collections | 获取所有文献集 | 返回文献集列表 |
| test_get_collection | 获取单个文献集 | 返回正确的文献集数据 |
| test_get_collection_items | 获取文献集条目 | 返回属于该文献集的条目列表 |
| test_get_collection_not_found | 文献集不存在 | 适当的错误处理 |

#### 标签和元数据测试

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_get_tags | 获取所有标签 | 返回标签列表 |
| test_get_pmid | 提取 PMID | 从 extra 字段正确解析 PMID |
| test_get_pmid_not_found | PMID 不存在 | 返回空字符串 |
| test_get_pmid_invalid_format | PMID 格式错误 | 适当的错误处理 |

#### 附件操作测试

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_get_item_file | 获取附件文件 | 返回二进制流对象 |
| test_get_item_file_compressed | 压缩附件处理 | 正确解压并返回内容 |
| test_get_item_attachment_href | 获取附件链接 | 返回有效的下载链接 |
| test_get_item_attachment_no_pdf | 非 PDF 附件 | 抛出 ZoteroLocalError |
| test_download_file | 下载文件到本地 | 文件正确保存到指定路径 |
| test_download_file_create_dir | 下载时创建目录 | 自动创建不存在的父目录 |
| test_upload_file | 上传文件 | 文件成功上传并返回条目信息 |
| test_upload_file_not_found | 文件不存在 | 抛出 ZoteroLocalError |
| test_upload_file_with_parent | 带父条目上传 | parentItem 参数正确传递 |

#### 工具方法测试

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_guess_mimetype | MIME 类型推断 | 正确识别常见文件类型 |
| test_guess_mimetype_unknown | 未知类型处理 | 返回默认 MIME 类型 |
| test_calculate_md5 | MD5 计算 | 计算结果准确 |
| test_copy_attachment_to_downloads | 复制附件到下载目录 | 文件正确复制到目标位置 |

### SearchMixin 测试（test_search.py）

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_search_items | 关键词搜索 | 返回匹配的条目列表 |
| test_search_items_no_results | 无结果搜索 | 返回空列表 |
| test_search_by_doi | DOI 搜索 | 精确匹配 DOI 字段 |
| test_search_by_doi_case_insensitive | DOI 大小写不敏感 | 忽略大小写匹配 |
| test_search_by_pmid | PMID 搜索 | 从 extra 字段匹配 PMID |
| test_search_by_pmid_no_match | PMID 无匹配 | 返回空列表 |
| test_search_by_title_exact | 标题精确匹配 | exact_match=True 时精确匹配 |
| test_search_by_title_partial | 标题部分匹配 | 默认支持部分匹配 |
| test_search_by_title_case_insensitive | 标题搜索忽略大小写 | 大小写不敏感 |
| test_search_error_handling | 搜索错误处理 | 抛出 ZoteroLocalError |

### FilesMixin 测试（test_files.py）

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_get_item_file_normal | 获取普通文件 | 返回正确的二进制流 |
| test_get_item_file_compressed | 获取压缩文件 | 自动解压缩 |
| test_copy_attachment_to_downloads | 复制附件 | 文件复制成功 |
| test_copy_attachment_custom_dir | 自定义目录复制 | 使用指定下载目录 |
| test_copy_attachment_create_dir | 创建目录 | 目标目录不存在时自动创建 |
| test_normalize_path_unix | Unix 路径规范化 | file:// URI 转换为绝对路径 |
| test_normalize_path_windows | Windows 路径规范化 | file:/// URI 正确处理 |
| test_normalize_path_url_encoded | URL 编码路径 | 正确解码特殊字符 |
| test_copy_file_error | 复制失败处理 | 抛出 ZoteroLocalError |

### NotesMixin 测试（test_notes.py）

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_get_note | 获取笔记 | 返回正确的笔记数据 |
| test_get_note_not_found | 笔记不存在 | 抛出 ZoteroLocalError |
| test_get_note_wrong_type | 非笔记类型条目 | 抛出错误提示非笔记 |
| test_get_item_notes | 获取条目的所有笔记 | 返回笔记列表，过滤非笔记条目 |
| test_get_item_notes_empty | 条目无笔记 | 返回空列表 |
| test_add_item_note | 添加笔记 | 笔记成功创建并关联到条目 |
| test_add_item_note_with_title | 带标题添加笔记 | title 参数正确传递 |
| test_add_item_note_html_content | HTML 格式笔记 | 支持 HTML 格式内容 |
| test_add_note_invalid_parent | 父条目不存在 | 抛出 ZoteroLocalError |
| test_add_note_api_error | API 错误处理 | 处理创建失败响应 |

### 异常类测试（test_exceptions.py）

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_exception_hierarchy | 异常继承关系 | 所有异常继承自 ZoteroLocalError |
| test_zotero_local_error | 基础异常 | 可以实例化和抛出 |
| test_connection_error | 连接错误 | 异常信息正确传递 |
| test_authentication_error | 认证错误 | 异常信息正确传递 |
| test_not_found_error | 资源未找到 | 异常信息正确传递 |
| test_api_error | API 错误 | 异常信息正确传递 |
| test_resource_not_found | ResourceNotFound 异常 | 异常信息正确传递 |

## 集成测试设计

### 工作流集成测试（test_workflows.py）

#### 端到端场景

| 测试场景 | 流程描述 | 验证点 |
|---------|---------|--------|
| test_search_and_get_note_workflow | 搜索条目并获取笔记 | 1. 搜索条目 2. 获取条目笔记 3. 验证笔记内容 |
| test_upload_and_download_workflow | 上传下载附件流程 | 1. 上传文件 2. 获取附件 3. 下载验证内容一致 |
| test_add_note_and_retrieve_workflow | 添加笔记并检索 | 1. 创建笔记 2. 通过条目获取笔记 3. 验证笔记存在 |
| test_collection_items_workflow | 文献集操作流程 | 1. 获取文献集 2. 获取文献集条目 3. 搜索特定条目 |
| test_multi_search_workflow | 多种搜索方式组合 | 1. 标题搜索 2. DOI 搜索 3. PMID 搜索 4. 结果一致性 |

### API 集成测试（test_api_integration.py）

测试与真实（或完整模拟的）Zotero API 的交互：

| 测试用例 | 测试目标 | 验证点 |
|---------|---------|--------|
| test_api_connection | API 连接性 | 成功连接到 Zotero 本地服务器 |
| test_api_error_responses | API 错误响应处理 | 各种 HTTP 错误码的处理 |
| test_api_rate_limiting | 速率限制处理 | 如果有速率限制，验证重试机制 |
| test_concurrent_requests | 并发请求 | Session 复用的线程安全性 |

## 测试数据和 Mock 策略

### Mock 响应数据结构

#### 样本条目数据（sample_item_data）

包含字段：
- key：条目唯一标识
- version：版本号
- data：条目主体数据
  - itemType：条目类型（journalArticle、book等）
  - title：标题
  - creators：作者列表
  - DOI：DOI 标识
  - extra：额外信息（包含 PMID）
  - tags：标签列表
  - collections：所属文献集
- links：相关链接
  - attachment：附件信息

#### 样本文献集数据（sample_collection_data）

包含字段：
- key：文献集 key
- version：版本号
- data：文献集数据
  - name：文献集名称
  - parentCollection：父文献集

#### 样本笔记数据（sample_note_data）

包含字段：
- key：笔记 key
- version：版本号
- data：笔记数据
  - itemType："note"
  - parentItem：父条目 key
  - note：笔记内容（HTML）
  - tags：标签

### requests-mock 使用策略

1. 按测试模块注册不同的 Mock endpoints
2. 使用 mocker.register_uri 预设响应
3. 支持多种响应状态（200、404、500等）
4. 使用 additional_matcher 实现复杂匹配逻辑
5. 验证请求调用次数和参数

### 测试文件准备

在 fixtures/test_files/ 目录下准备：
- sample.pdf：测试 PDF 文件
- sample.txt：测试文本文件
- sample.zip：测试压缩文件
- large_file.pdf：测试大文件处理

## 测试执行策略

### 测试分类标记

使用 pytest.mark 对测试进行分类：

| 标记 | 用途 | 示例 |
|------|-----|------|
| @pytest.mark.unit | 单元测试 | 所有 unit/ 目录测试 |
| @pytest.mark.integration | 集成测试 | 所有 integration/ 目录测试 |
| @pytest.mark.slow | 慢速测试 | 涉及文件 I/O 的测试 |
| @pytest.mark.network | 需要网络的测试 | 真实 API 调用测试（可选） |

### 执行命令设计

| 命令 | 用途 |
|------|-----|
| pytest | 运行所有测试 |
| pytest tests/unit | 仅运行单元测试 |
| pytest tests/integration | 仅运行集成测试 |
| pytest -m "not slow" | 跳过慢速测试 |
| pytest --cov=src/zoteroapi | 生成覆盖率报告 |
| pytest --cov=src/zoteroapi --cov-report=html | 生成 HTML 覆盖率报告 |
| pytest -n auto | 并行执行测试 |
| pytest -v | 详细输出模式 |
| pytest -k "test_search" | 运行名称匹配的测试 |

### 持续集成考虑

为 CI/CD 流程设计测试命令：
- 快速测试：仅运行单元测试，跳过慢速测试
- 完整测试：运行所有测试并生成覆盖率报告
- 失败快速反馈：使用 -x 或 --maxfail=1 参数

## 覆盖率目标

### 覆盖率指标

| 模块 | 目标覆盖率 | 优先级 |
|------|-----------|--------|
| base_client.py | 90% | 高 |
| client.py | 85% | 高 |
| mixins/search.py | 90% | 高 |
| mixins/files.py | 85% | 中 |
| mixins/notes.py | 90% | 高 |
| exceptions.py | 100% | 高 |
| 整体项目 | 85% | - |

### 覆盖率排除项

不需要覆盖的代码：
- __init__.py 中的简单导入语句
- 调试用的 print 语句（如果存在）
- 平台特定的错误处理分支（如果难以测试）

## 测试质量保障

### 测试原则

1. 独立性：每个测试用例独立运行，不依赖其他测试
2. 可重复性：多次运行结果一致
3. 快速性：单元测试应在秒级完成
4. 清晰性：测试名称和结构清晰表达测试意图
5. 完整性：覆盖正常流程、边界条件、异常情况

### 断言策略

- 使用明确的断言消息
- 优先使用 pytest 的增强断言（assert）
- 对复杂对象使用结构化断言
- 验证异常类型和消息内容

### 命名规范

- 测试文件：test_<module_name>.py
- 测试类：Test<FeatureName>（可选）
- 测试函数：test_<action>_<expected_result>
- Fixture：使用描述性名称，体现提供的资源

## 实现优先级

### 第一阶段：基础框架

1. 创建测试目录结构
2. 配置 pytest.ini 和 pyproject.toml
3. 实现 conftest.py 核心 fixtures
4. 准备 Mock 数据和样本响应

### 第二阶段：核心单元测试

1. test_base_client.py
2. test_exceptions.py
3. test_client.py（条目和文献集基础操作）

### 第三阶段：Mixin 测试

1. test_search.py
2. test_notes.py
3. test_files.py

### 第四阶段：完善和集成

1. 补充 test_client.py 剩余用例
2. 实现集成测试
3. 覆盖率分析和补充
4. 文档和使用示例

## 维护和扩展

### 测试维护指南

- 代码更改时同步更新测试
- 新功能必须包含相应测试
- 定期审查和重构测试代码
- 保持 Mock 数据与实际 API 响应同步

### 扩展考虑

- 性能测试：为关键操作添加性能基准测试
- 兼容性测试：测试不同 Python 版本（3.11+）
- 安全测试：验证敏感数据处理
- 文档测试：使用 doctest 验证文档示例

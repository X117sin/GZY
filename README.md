# AI数据分析助手

一个基于Streamlit的智能数据分析工具，支持多种文件格式的数据处理和AI驱动的数据分析。

## 🌟 主要功能

### 📊 多格式数据支持
- **Excel文件**: .xlsx, .xls格式
- **CSV文件**: 标准CSV格式
- **JSON文件**: 结构化JSON数据
- **文本文件**: .txt格式
- **混合格式**: 同时分析多种格式文件

### 🤖 AI智能分析
- **多模型支持**: DeepSeek、OpenAI GPT、Claude等主流AI模型
- **自然语言查询**: 用中文描述分析需求
- **智能图表生成**: 自动生成柱状图、折线图等可视化图表
- **数据洞察**: AI驱动的数据模式识别和趋势分析

### 📈 数据可视化
- **柱状图**: 分类数据对比分析
- **折线图**: 趋势变化展示
- **数据表格**: 清晰的数据展示
- **交互式图表**: 基于Streamlit的动态图表

### 💾 历史记录管理
- **分析历史**: 保存所有分析记录
- **历史统计**: 查看分析次数和使用情况
- **一键清理**: 快速清除历史数据
- **SQLite存储**: 本地数据库存储，安全可靠

### 🎨 现代化UI设计
- **双栏布局**: 主内容区域 + 侧边栏工具
- **响应式设计**: 适配不同屏幕尺寸
- **中文界面**: 完全本土化的用户体验
- **自定义样式**: 美观的界面设计

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd GZY
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置API密钥**
在侧边栏的"AI模型配置"中输入您的API密钥：
- DeepSeek API Key
- OpenAI API Key  
- Anthropic API Key
- 或自定义API配置

4. **启动应用**
```bash
streamlit run main.py
```

5. **访问应用**
打开浏览器访问: http://localhost:8501

## 📖 使用指南

### 标准数据分析
1. 在侧边栏选择"标准数据分析"
2. 上传您的数据文件（支持Excel、CSV、JSON、TXT）
3. 配置AI模型和API密钥
4. 在分析输入框中用中文描述您的分析需求
5. 点击"开始分析"获取结果

### 混合格式文件分析
1. 选择"混合格式文件分析"
2. 同时上传多个不同格式的文件
3. AI将自动识别文件格式并进行综合分析
4. 获取跨文件的数据洞察

### 历史记录管理
- **查看历史**: 在"数据存储与历史记录"中查看所有分析记录
- **统计信息**: 查看分析次数、使用频率等统计数据
- **清理数据**: 一键清除不需要的历史记录

## 📁 项目结构

```
GZY/
├── main.py              # 主应用程序
├── utils.py             # 核心功能模块
├── common.py            # 通用工具函数
├── requirements.txt     # 项目依赖
├── .streamlit/
│   └── config.toml      # Streamlit配置
├── analysis_history.db  # 历史记录数据库
└── README.md           # 项目说明文档
```

## ⚙️ 配置说明

### Streamlit配置 (.streamlit/config.toml)
```toml
[theme]
base = "light"
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
maxUploadSize = 200

[logger]
level = "error"
```

### 支持的文件格式
- **Excel**: .xlsx, .xls (最大64MB)
- **CSV**: 标准逗号分隔值文件
- **JSON**: 结构化JSON数据文件
- **TXT**: 纯文本文件
- **混合**: 同时处理多种格式

## 🛠️ 技术栈

- **前端框架**: Streamlit
- **数据处理**: Pandas, OpenPyXL
- **AI集成**: LangChain
- **数据可视化**: Matplotlib, Altair
- **数据存储**: SQLite3
- **异步处理**: aiohttp

## 📦 主要依赖

```
streamlit>=1.28.0
pandas>=2.0.0
langchain>=0.1.0
matplotlib>=3.7.0
openpyxl>=3.1.0
aiohttp>=3.9.0
altair>=5.0.0
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## ❓ 常见问题

### Q: 如何获取API密钥？
A: 
- **DeepSeek**: 访问 [DeepSeek官网](https://platform.deepseek.com) 注册获取
- **OpenAI**: 访问 [OpenAI官网](https://platform.openai.com) 注册获取
- **Anthropic**: 访问 [Anthropic官网](https://console.anthropic.com) 注册获取

### Q: 支持哪些数据分析类型？
A: 支持描述性统计、趋势分析、相关性分析、分类汇总、数据清洗、异常检测等多种分析类型。

### Q: 文件上传大小限制？
A: 单个文件最大支持200MB，建议使用压缩格式以提高处理效率。

### Q: 如何处理中文数据？
A: 系统完全支持中文数据处理，包括中文列名、中文内容分析和中文图表标签。

---

**开发团队**: AI数据分析助手开发组  
**最后更新**: 2024年

如有问题或建议，欢迎提交Issue或联系开发团队！
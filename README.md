# AI私厨 (AI Private Chef)

智能烹饪助手 - 基于LangChain和LangGraph的AI烹饪推荐系统

## 项目简介

AI私厨是一个智能烹饪助手系统，利用大语言模型和多智能体架构，为用户提供个性化的烹饪建议和食谱推荐。

## 主要功能

- 🤖 **多智能体系统** - 基于LangGraph的个人厨师智能体
- 💬 **对话交互** - 实时聊天界面，支持烹饪咨询
- 📸 **图像识别** - 支持上传食材图片进行识别
- 🔍 **网络搜索** - 集成Tavily搜索获取最新食谱信息
- 💾 **数据持久化** - SQLite数据库存储对话历史
- ☁️ **云存储** - 阿里云OSS集成支持

## 技术栈

- **后端框架**: FastAPI + Uvicorn
- **AI框架**: LangChain + LangGraph
- **前端**: Vue 3 + Tailwind CSS
- **数据库**: SQLite
- **云服务**: 阿里云OSS
- **其他**: Playwright, Pillow

## 项目结构

```
.
├── app/
│   ├── agents/           # 智能体定义
│   ├── api/              # API路由
│   ├── models/           # 数据模型
│   ├── common/           # 通用工具
│   ├── static/           # 前端资源
│   └── main.py           # 应用入口
├── tests/                # 测试文件
├── resources/            # 资源文件
├── pyproject.toml        # 项目配置
└── langgraph.json        # LangGraph配置
```

## 快速开始

### 环境要求

- Python >= 3.10
- uv (Python包管理工具)

### 安装依赖

```bash
uv sync
```

### 运行应用

```bash
python app/main.py
```

应用将在 `http://localhost:8000` 启动

## 配置

创建 `.env` 文件配置必要的环境变量：

```env
OPENAI_API_KEY=your_api_key
TAVILY_API_KEY=your_tavily_key
# 其他配置...
```

## 测试

```bash
pytest tests/
```

## 许可证

MIT License

## 作者

AI Private Chef Team

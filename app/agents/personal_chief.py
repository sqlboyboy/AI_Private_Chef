# ============================================================
# AI 私厨 Agent - 智能食材分析系统
# ============================================================

import os
import sys
import io

# 修复 Windows 中的 Unicode 输出问题
# 仅在直接运行时修改，避免在导入时修改导致 pytest 失败
def _setup_windows_encoding():
    """设置 Windows 下的 UTF-8 编码"""
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except Exception:
            pass  # 如果在 pytest 等环境中失败，忽略

# 在导入前设置编码（用于模块导入时的打印）
if sys.platform == "win32":
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    except Exception:
        pass

from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage

# 加载环境变量
load_dotenv()

# ============================================================
# 1. 验证必要的环境变量
# ============================================================
required_env_vars = ["TAVILY_API_KEY", "ZHIPUAI_API_KEY", "ZHIPUAI_BASE_URL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ 错误：缺少以下环境变量: {', '.join(missing_vars)}")
    print("📝 请在 .env 文件中配置这些变量")
    sys.exit(1)

# ============================================================
# 2. 初始化 Web 搜索工具
# ============================================================
try:
    tavily_tool = TavilySearch(
        max_results=5,
        topic="general",
        tavily_api_key=os.getenv("TAVILY_API_KEY")
    )
    print("✅ TavilySearch 初始化成功")
except Exception as e:
    print(f"❌ 初始化 TavilySearch 失败: {e}")
    sys.exit(1)

# ============================================================
# 3. 初始化 LLM 模型（智谱 AI GLM）
# ============================================================
try:
    model = init_chat_model(
        model="glm-4.6v",
        model_provider="openai",  # 智谱AI兼容OpenAI API
        temperature=0.5,
        timeout=60,
        max_tokens=1000,
        api_key=os.getenv("ZHIPUAI_API_KEY"),
        base_url=os.getenv("ZHIPUAI_BASE_URL")
    )
    print("✅ LLM 模型初始化成功")
except Exception as e:
    print(f"❌ 初始化模型失败: {e}")
    sys.exit(1)

# ============================================================
# 4. 定义 Web 搜索工具
# ============================================================
@tool
def web_search(query: str) -> str:
    """
    搜索食谱、食材营养信息或烹饪方法。
    
    Args:
        query: 搜索查询字符串
        
    Returns:
        搜索结果文本
    """
    try:
        results = tavily_tool.run(query)
        return results
    except Exception as e:
        return f"搜索失败: {e}"


# ============================================================
# 5. 定义系统 Prompt
# ============================================================
system_prompt = """
你是一名专业的私人厨师。收到用户提供的食材照片或清单后，请按以下流程操作：

1. 识别和评估食材：
   - 若用户提供照片，首先辨识所有可见食材
   - 基于食材的外观状态，评估其新鲜度与可用量
   - 整理出一份"当前可用食材清单"

2. 智能食谱检索：
   - 优先调用 web_search 工具
   - 以"可用食材清单"为核心关键词查找可行菜谱

3. 多维度评估与排序：
   - 从营养价值和制作难度两个维度对候选食谱打分
   - 根据得分排序，制作简单且营养丰富的排名靠前

4. 结构化方案输出：
   - 把排序后的食谱整理为清晰的建议报告
   - 包含食谱信息、得分、推荐理由、参考图片
   - 帮助用户快速做出决策

提示：优先调用 web_search 工具搜索食谱，搜索不到的情况下才能自己发挥。
"""

# ============================================================
# 6. 记忆模块
# ============================================================
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# 连接sqlite
connection = sqlite3.connect("resources/personal_chief.db", check_same_thread=False)
# 初始化checkpointer
checkpointer = SqliteSaver(connection)
# 自动建表
checkpointer.setup()

# ============================================================
# 7. 初始化 Agent
# ============================================================
try:
    agent = create_agent(
        model=model,
        tools=[web_search],
        system_prompt=system_prompt,
        checkpointer=checkpointer
    )
    print("✅ Agent 初始化成功")
except Exception as e:
    print(f"❌ 创建 Agent 失败: {e}")
    sys.exit(1)


# ============================================================
# 8. 测试 Agent
# ============================================================
def test_agent():
    """测试 Agent 功能"""
    try:
        print("\n" + "="*60)
        print("🤖 启动 AI 私厨 Agent 测试...")
        print("="*60)

        # 准备多模态消息
        multimodal_message = HumanMessage(
            content=[
                {
                    "type": "image",
                    "url": "https://img.freepik.com/free-photo/arrangement-different-foods-organized-fridge_23-2149099882.jpg"
                },
                {
                    "type": "text",
                    "text": "帮我看看这些食材能做什么？"
                }
            ]
        )

        config = {"configurable": {"thread_id": "2"}}

        print("\n🤖 Agent 正在处理请求...\n")
        response = agent.invoke(
            {"messages": [multimodal_message]},
            config
        )

        print("\n✅ Agent 响应:")

        # 友好打印
        for message in response['messages']:
            message.pretty_print()

        return response

    except Exception as e:
        print(f"\n❌ Agent 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================
# 8. 主入口
# ============================================================
if __name__ == "__main__":
    _setup_windows_encoding()  # 仅在直接运行时设置编码
    print("\n🍳 AI 私厨 Agent 启动中...\n")
    test_agent()
    print("\n✅ 测试完成！")


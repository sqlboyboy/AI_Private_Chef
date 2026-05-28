# ============================================================
# AI 私厨 Agent - LangSmith 集成版本
# 用于调试、跟踪和监控 Agent 的执行过程
# ============================================================

import os
import sys
import io

# 修复 Windows 中的 Unicode 输出问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.messages import HumanMessage

# 加载环境变量
load_dotenv()

# 设置 LangSmith 用于跟踪
# 启用 LangSmith 追踪功能
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")

# 安全地设置 API Key
if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")

os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "ai-chef-agent")

print("=" * 70)
print("🍳 AI 私厨 Agent - LangSmith 集成版本")
print("=" * 70)

# ============================================================
# 1. 验证必要的环境变量
# ============================================================
print("\n[1] 验证环境变量...")

required_env_vars = ["TAVILY_API_KEY", "ZHIPUAI_API_KEY", "ZHIPUAI_BASE_URL"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ 错误：缺少以下环境变量: {', '.join(missing_vars)}")
    sys.exit(1)

print("✅ 所有必需的环境变量已配置")

# 验证 LangSmith 配置
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
if langsmith_api_key:
    print(f"✅ LangSmith 已配置")
    print(f"   - API Key: {'*' * 20}...{langsmith_api_key[-4:]}")
    print(f"   - Project: {os.getenv('LANGSMITH_PROJECT', 'ai-chef-agent')}")
else:
    print("⚠️  LangSmith 未配置，继续运行但不启用追踪功能")

# ============================================================
# 2. 初始化 Web 搜索工具
# ============================================================
print("\n[2] 初始化 Web 搜索工具...")

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
print("\n[3] 初始化 LLM 模型...")

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
    print(f"   - 模型: glm-4.6v (智谱 AI)")
    print(f"   - 温度: 0.5")
    print(f"   - Max Tokens: 1000")
except Exception as e:
    print(f"❌ 初始化模型失败: {e}")
    sys.exit(1)

# ============================================================
# 4. 定义 Web 搜索工具
# ============================================================
print("\n[4] 定义工具函数...")

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

print("✅ Web 搜索工具已定义")

# ============================================================
# 5. 定义系统 Prompt
# ============================================================
print("\n[5] 配置 System Prompt...")

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

print("✅ System Prompt 已配置")

# ============================================================
# 6. 初始化 Agent
# ============================================================
print("\n[6] 创建 Agent...")

try:
    agent = create_agent(
        model=model,
        tools=[web_search],
        system_prompt=system_prompt
    )
    print("✅ Agent 初始化成功")
    print(f"   - 工具数: 1 (web_search)")
    print(f"   - 模型集成: ✅")
except Exception as e:
    print(f"❌ 创建 Agent 失败: {e}")
    sys.exit(1)

# ============================================================
# 7. LangSmith 追踪配置
# ============================================================
print("\n[7] 配置 LangSmith 追踪...")

from langsmith import traceable

@traceable(name="ai_chef_complete_pipeline")
def run_ai_chef_pipeline(user_message: str, image_url: str = None):
    """
    完整的 AI 私厨 Agent 管道，带 LangSmith 追踪
    
    Args:
        user_message: 用户的文本消息
        image_url: 可选的图片 URL
    """
    print(f"\n📝 用户消息: {user_message}")
    if image_url:
        print(f"🖼️  图片 URL: {image_url}")
    
    # 准备多模态消息
    content = []
    if image_url:
        content.append({
            "type": "image",
            "url": image_url
        })
    
    content.append({
        "type": "text",
        "text": user_message
    })
    
    multimodal_message = HumanMessage(content=content)
    
    # 配置
    config = {"configurable": {"thread_id": "ai-chef-001"}}
    
    # 调用 Agent
    print("\n🤖 Agent 正在处理请求...\n")
    response = agent.invoke(
        {"messages": [multimodal_message]},
        config
    )
    
    return response

print("✅ LangSmith 追踪已配置")

# ============================================================
# 8. 测试执行
# ============================================================
def test_execution():
    """测试 Agent 功能"""
    
    print("\n" + "=" * 70)
    print("🧪 开始测试执行 (启用 LangSmith 追踪)")
    print("=" * 70)
    
    try:
        # 测试用例 1: 带图片的查询
        print("\n📌 测试用例 1: 带图片的食材分析")
        print("-" * 70)
        
        response = run_ai_chef_pipeline(
            user_message="帮我看看这些食材能做什么？",
            image_url="https://img.freepik.com/free-photo/arrangement-different-foods-organized-fridge_23-2149099882.jpg"
        )
        
        print("\n✅ 测试用例 1 完成")
        print("-" * 70)
        
        # 提取响应
        if "messages" in response and len(response["messages"]) > 0:
            messages = response["messages"]
            
            # 查找 AI 的最终响应
            for msg in reversed(messages):
                if hasattr(msg, 'content') and isinstance(msg.content, str):
                    final_response = msg.content
                    print(f"\n🤖 Agent 最终响应摘要:")
                    print(final_response[:500] + ("..." if len(final_response) > 500 else ""))
                    break
        
        return response
        
    except Exception as e:
        print(f"\n❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================
# 9. 生成 LangSmith 报告
# ============================================================
def generate_langsmith_report():
    """生成 LangSmith 调试信息"""
    
    print("\n" + "=" * 70)
    print("📊 LangSmith 追踪信息")
    print("=" * 70)
    
    api_key_status = "✅ 已配置" if os.getenv("LANGSMITH_API_KEY") else "⚠️  未配置"
    tracing_status = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    
    print(f"\n配置信息:")
    print(f"  - LangSmith API Key: {api_key_status}")
    print(f"  - 追踪启用: {'✅ 是' if tracing_status else '❌ 否'}")
    print(f"  - 项目名称: {os.getenv('LANGSMITH_PROJECT', '默认')}")
    print(f"  - 端点: {os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com')}")
    
    if api_key_status == "✅ 已配置":
        print(f"\n📍 LangSmith 可视化:")
        print(f"  🔗 访问地址: https://smith.langchain.com")
        print(f"  📊 项目: {os.getenv('LANGSMITH_PROJECT', '默认')}")
        print(f"  🔍 所有调用将被自动追踪和记录")


# ============================================================
# 10. 主入口
# ============================================================
if __name__ == "__main__":
    print("\n[8] 启动测试执行...\n")
    
    # 显示 LangSmith 信息
    generate_langsmith_report()
    
    print("\n" * 1)
    
    # 执行测试
    result = test_execution()
    
    print("\n" + "=" * 70)
    print("✅ 测试完成!")
    print("=" * 70)
    
    print("\n💡 提示:")
    print("  - 所有调用已通过 LangSmith 进行追踪")
    print("  - 访问 https://smith.langchain.com 查看详细的调用链")
    print("  - 可以在 LangSmith 中查看性能指标、错误和日志")



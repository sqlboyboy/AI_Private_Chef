import io
from contextlib import redirect_stdout
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest
from app.agents.personal_chief import agent
from app.common.logger import logger
from app.common.validators import validate_message, validate_thread_id, validate_image_url
from app.common.exceptions import ValidationException

router = APIRouter()

def capture_pretty_print(messages):
    """
    捕获 pretty_print() 的输出内容

    Args:
        messages: LangChain 消息列表

    Returns:
        str: 格式化的消息输出
    """
    output = io.StringIO()

    with redirect_stdout(output):
        for message in messages:
            try:
                message.pretty_print()
            except Exception as e:
                logger.warning(f"⚠️ pretty_print 失败: {e}")
                output.write(f"[Error printing message: {e}]\n")

    return output.getvalue()

def serialize_messages(messages):
    """
    将消息对象序列化为可 JSON 序列化的格式

    Args:
        messages: LangChain 消息列表

    Returns:
        list: 序列化后的消息列表
    """
    result = []
    for message in messages:
        try:
            if hasattr(message, 'model_dump'):
                result.append(message.model_dump())
            elif hasattr(message, 'dict'):
                result.append(message.dict())
            else:
                result.append({
                    "type": type(message).__name__,
                    "content": str(message)
                })
        except Exception as e:
            logger.error(f"❌ 消息序列化失败: {e}")
            result.append({
                "type": type(message).__name__,
                "error": str(e)
            })
    return result

@router.post("")
async def chat_message(request: ChatRequest):
    """
    处理用户消息的 API 端点 - 集成 Agent

    Args:
        request: ChatRequest 对象，包含 message、image_url、thread_id

    Returns:
        dict: 包含 status、pretty_print、messages 的响应

    Raises:
        HTTPException: 处理失败时返回 400 或 500 错误
    """
    try:
        from langchain.messages import HumanMessage

        # ============================================================
        # 1. 验证请求数据
        # ============================================================
        try:
            message = validate_message(request.message)
            thread_id = validate_thread_id(request.thread_id)
            image_url = validate_image_url(request.image_url) if request.image_url else None
        except ValidationException as e:
            logger.warning(f"⚠️ 数据验证失败: {e}")
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

        logger.info(f"📨 收到消息 - thread_id: {thread_id}, 消息长度: {len(message)}")

        # ============================================================
        # 2. 构建消息内容
        # ============================================================
        content = [{"type": "text", "text": message}]

        if image_url:
            logger.info(f"🖼️ 包含图片 URL: {image_url}")
            content.insert(0, {"type": "image", "url": image_url})

        # ============================================================
        # 3. 创建人类消息
        # ============================================================
        human_message = HumanMessage(content=content)

        # ============================================================
        # 4. 配置线程 ID
        # ============================================================
        config = {"configurable": {"thread_id": thread_id}}

        # ============================================================
        # 5. 调用 Agent
        # ============================================================
        logger.info("🤖 调用 Agent 处理消息...")
        response = agent.invoke(
            {"messages": [human_message]},
            config
        )

        logger.info("✅ Agent 处理完成")

        # ============================================================
        # 6. 提取最后一条 AI 消息（只返回纯文本内容）
        # ============================================================
        from langchain_core.messages import AIMessage

        ai_response = ""
        for msg in reversed(response.get('messages', [])):
            if isinstance(msg, AIMessage):
                content = msg.content
                if isinstance(content, str):
                    ai_response = content.strip()
                elif isinstance(content, list):
                    texts = [
                        c.get('text', '')
                        for c in content
                        if isinstance(c, dict) and c.get('type') == 'text'
                    ]
                    ai_response = '\n'.join(t for t in texts if t).strip()
                if ai_response:
                    break

        if not ai_response:
            ai_response = "抱歉，我无法处理您的请求。"

        logger.info(f"📤 返回 AI 回复，长度: {len(ai_response)}")

        return {
            "status": "success",
            "message": ai_response,
            "thread_id": thread_id
        }

    except HTTPException:
        # 直接抛出 HTTP 异常
        raise

    except Exception as e:
        logger.error(f"❌ Chat API 处理失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"处理消息失败: {str(e)}"
        )

@router.get("/test")
async def test_endpoint():
    """
    测试端点 - 检查 Chat API 是否正常工作

    Returns:
        dict: 测试状态信息
    """
    logger.info("🧪 Chat API 测试")
    return {
        "message": "Chat API is working",
        "status": "ok"
    }
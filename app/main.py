from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from dotenv import load_dotenv
from app.api.v1 import chat
from app.api.v1 import oss
from app.common.logger import setup_logging

# 加载环境变量
load_dotenv()

# 初始化日志配置
setup_logging()

app = FastAPI(
    title="Personal Chief API",
    description="私厨",
    version="0.1.0"
)

# 1. 配置跨域资源共享 (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 挂载路由
app.include_router(chat.router, prefix="/api/v1/chat", tags=["对话"])
app.include_router(oss.router, prefix="/api/v1", tags=["申请上传签名url"])

# 3. 配置静态文件服务
static_dir = os.path.join(os.path.dirname(__file__), "static")

# 4. 根路由 - 返回 index.html
@app.get("/")
async def root():
    """返回主页"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not found")

# 5. SPA 路由 - 非 API 路径都返回 index.html
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    SPA 路由处理 - 返回 index.html
    API 路径由上面的路由处理，其余路径交给前端 Vue Router
    """
    # API 路径不走 SPA fallback
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    # 静态文件路径
    if full_path.startswith("static/"):
        file_path = os.path.join(static_dir, full_path[7:])  # 去掉 "static/" 前缀
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    # 其他路径返回 index.html
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8001, reload=True)

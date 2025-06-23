"""
FastAPI main application for AI Interviewer Agent
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import speech, llm, scraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")

# Global connection manager
manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    logger.info("Starting AI Interviewer Agent...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Server will run on {settings.host}:{settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Interviewer Agent...")

# Create FastAPI application
app = FastAPI(
    title="AI Interviewer Agent",
    description="An AI-powered interview simulator with speech recognition and code analysis",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

# Templates
templates = Jinja2Templates(directory="ui/templates")

# Include API routers
app.include_router(speech.router, prefix="/api/speech", tags=["speech"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(scraper.router, prefix="/api/scraper", tags=["scraper"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application interface"""
    return """
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 面試模擬器</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="/static/css/main.css" rel="stylesheet">
    </head>
    <body>
        <div id="app">
            <nav class="navbar navbar-dark bg-primary">
                <div class="container-fluid">
                    <span class="navbar-brand mb-0 h1">🤖 AI 面試模擬器</span>
                    <div class="d-flex">
                        <button id="start-interview" class="btn btn-success me-2">開始面試</button>
                        <button id="stop-interview" class="btn btn-danger" disabled>結束面試</button>
                    </div>
                </div>
            </nav>
            
            <div class="container-fluid mt-3">
                <div class="row">
                    <!-- Control Panel -->
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-header">
                                <h5>控制面板</h5>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label for="interview-type" class="form-label">面試類型</label>
                                    <select class="form-select" id="interview-type">
                                        <option value="technical">技術面試</option>
                                        <option value="behavioral">行為面試</option>
                                        <option value="system_design">系統設計</option>
                                    </select>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="scraping-interval" class="form-label">抓取間隔 (秒)</label>
                                    <input type="number" class="form-control" id="scraping-interval" value="10" min="5" max="60">
                                </div>
                                
                                <div class="mb-3">
                                    <label for="leetcode-url" class="form-label">LeetCode URL</label>
                                    <input type="url" class="form-control" id="leetcode-url" placeholder="貼上 LeetCode 題目連結">
                                </div>
                                
                                <div class="d-grid gap-2">
                                    <button id="manual-scrape" class="btn btn-outline-primary">手動抓取程式碼</button>
                                    <button id="toggle-auto-scrape" class="btn btn-outline-warning">開啟自動抓取</button>
                                </div>
                                
                                <hr>
                                
                                <div class="mb-3">
                                    <label class="form-label">音頻控制</label>
                                    <div class="d-grid gap-2">
                                        <button id="start-recording" class="btn btn-outline-success">🎤 開始錄音</button>
                                        <button id="stop-recording" class="btn btn-outline-danger" disabled>⏹️ 停止錄音</button>
                                    </div>
                                </div>
                                
                                <div class="mb-3">
                                    <label for="volume-control" class="form-label">音量控制</label>
                                    <input type="range" class="form-range" id="volume-control" min="0" max="100" value="80">
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Chat Interface -->
                    <div class="col-md-6">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5>對話區域</h5>
                            </div>
                            <div class="card-body d-flex flex-column">
                                <div id="chat-messages" class="flex-grow-1 overflow-auto mb-3" style="height: 400px;">
                                    <div class="alert alert-info">
                                        <strong>面試官：</strong> 您好！歡迎參加今天的面試。請先自我介紹一下吧！
                                    </div>
                                </div>
                                
                                <div class="input-group">
                                    <input type="text" id="message-input" class="form-control" placeholder="輸入您的回答..." disabled>
                                    <button id="send-message" class="btn btn-primary" disabled>發送</button>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Code Viewer -->
                    <div class="col-md-3">
                        <div class="card h-100">
                            <div class="card-header">
                                <h5>程式碼檢視器</h5>
                            </div>
                            <div class="card-body">
                                <div id="code-display" class="bg-dark text-light p-3 rounded" style="height: 400px; overflow-y: auto;">
                                    <pre><code>// 這裡會顯示抓取到的程式碼
// 請在 LeetCode 中開始解題...</code></pre>
                                </div>
                                
                                <div class="mt-3">
                                    <small class="text-muted">
                                        最後更新: <span id="last-update">未抓取</span>
                                    </small>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script src="/static/js/websocket.js"></script>
        <script src="/static/js/audio.js"></script>
        <script src="/static/js/main.js"></script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for real-time communication"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            logger.info(f"Received WebSocket message: {data}")
            
            # Echo message back (you can process this with LLM)
            await manager.send_personal_message(f"Echo: {data}", websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "debug": settings.debug
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    ) 
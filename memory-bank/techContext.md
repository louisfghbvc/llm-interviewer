# 技術環境與開發設定

## 技術堆疊

### 後端技術
- **Python 3.8+**: 主要開發語言
- **Flask 2.3+**: Web 框架
- **Google Generative AI**: LLM 整合 (Gemini API)
- **Flask-CORS**: 跨域請求支援

### 程式碼驗證工具
- **clang++**: C++ 語法驗證 (系統依賴)
- **Python AST**: Python 語法解析
- **正則表達式**: 通用語法檢查

### 開發工具
- **VS Code/Cursor**: 主要開發環境
- **Git**: 版本控制
- **虛擬環境**: Python 依賴隔離

## 環境設定

### 本地開發環境

#### 必要系統依賴
```bash
# macOS (使用 Homebrew)
brew install llvm  # 提供 clang++

# Ubuntu/Debian
sudo apt install clang

# CentOS/RHEL
sudo yum install clang
```

#### Python 虛擬環境設定
```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

#### 必要的環境變數
```bash
export GEMINI_API_KEY="your_api_key_here"
export FLASK_ENV="development"
export FLASK_DEBUG="True"
```

### API 金鑰配置

#### Google Gemini API
1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 創建新的 API 金鑰
3. 設定環境變數或使用 `.env` 檔案

#### 設定檔案範例 (.env)
```bash
GEMINI_API_KEY=AIza...
FLASK_PORT=5000
FLASK_HOST=0.0.0.0
DEBUG_MODE=True
```

## 依賴管理

### requirements.txt
```
Flask==2.3.3
Flask-CORS==4.0.0
google-generativeai==0.3.1
python-dotenv==1.0.0
```

### 依賴說明
- **Flask**: Web 框架核心
- **Flask-CORS**: 支援前端跨域請求
- **google-generativeai**: Gemini API 官方客戶端
- **python-dotenv**: 環境變數管理

## 開發環境設定

### 專案結構
```
interviewer-agent/
├── main.py              # Flask 應用入口
├── config.py            # 配置管理
├── llm_client.py        # Gemini API 整合
├── interview_manager.py # 面試邏輯
├── code_handler.py      # 程式碼分析
├── requirements.txt     # Python 依賴
├── .env                 # 環境變數 (本地)
├── .env.example         # 環境變數範例
├── venv/               # 虛擬環境
└── README.md           # 專案文檔
```

### VS Code 配置建議

#### settings.json
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

#### launch.json (偵錯配置)
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Flask Debug",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "env": {
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "console": "integratedTerminal"
        }
    ]
}
```

## 技術限制與約束

### 系統要求
- **Python 3.8+**: 支援 typing 和現代語法
- **clang++**: C++ 程式碼驗證需要
- **網路連線**: Gemini API 調用需要

### API 限制
- **Gemini API**: 
  - 免費版每分鐘 60 次請求
  - 每日請求量限制
  - 回應大小限制

### 效能約束
- **同步架構**: 單請求處理，不支援高併發
- **記憶體儲存**: 伺服器重啟會遺失會話資料
- **無持久化**: 不支援資料長期儲存

## 開發工作流程

### 1. 本地開發
```bash
# 啟動開發環境
source venv/bin/activate
export GEMINI_API_KEY="your_key"
python main.py
```

### 2. 測試流程
```bash
# 健康檢查
curl http://localhost:5000/api/health

# 測試 LLM 連線
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "test"}'

# 測試程式碼驗證
curl -X POST http://localhost:5000/api/validate_code \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello World\")", "language": "python"}'
```

### 3. 除錯技巧
- **Flask 除錯模式**: 自動重載和錯誤追蹤
- **日誌輸出**: print() 用於快速除錯
- **API 測試**: 使用 curl 或 Postman 測試端點
- **錯誤追蹤**: 檢查 Flask 控制台輸出

## 部署考量

### 生產環境需求
- **WSGI 伺服器**: Gunicorn 或 uWSGI
- **反向代理**: Nginx 或 Apache
- **環境變數**: 安全的金鑰管理
- **監控系統**: 基礎的健康檢查

### 安全考量
- **API 金鑰**: 絕不提交到版本控制
- **輸入驗證**: 所有用戶輸入都需驗證
- **錯誤處理**: 不洩露敏感系統資訊
- **CORS 設定**: 限制允許的來源網域

### 擴展性準備
- **配置外部化**: 支援不同環境配置
- **日誌標準化**: 結構化日誌輸出
- **健康檢查**: 完整的系統狀態監控
- **優雅關閉**: 處理 SIGTERM 信號 
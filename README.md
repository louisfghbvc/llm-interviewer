# 🤖 AI 面試模擬器

一個基於 Gemini LLM 的智能面試工具，支援語音對話、程式碼實時抓取與分析。

## ✨ 主要功能

### 🎙️ 語音處理
- **語音轉文字 (STT)**: 支援 OpenAI Whisper 和 Google Speech-to-Text
- **文字轉語音 (TTS)**: 支援 Edge TTS、Google TTS 和 OpenAI TTS
- **即時語音識別**: 支援多語言，降噪處理
- **音量控制**: 可調整語音播放音量

### 🧠 智能面試官
- **Gemini LLM 整合**: 使用 Google Gemini API 作為面試官
- **多種面試類型**: 技術面試、行為面試、系統設計面試
- **動態問題生成**: 根據候選人回答調整面試難度
- **程式碼分析**: 即時分析程式碼品質和邏輯

### 🌐 網站內容抓取
- **LeetCode 支援**: 即時抓取 LeetCode 解題程式碼
- **自動/手動抓取**: 支援定時自動抓取或手動觸發
- **多平台支援**: 可擴展支援其他程式平台
- **反爬蟲處理**: 智能處理網站反爬蟲機制

### 💬 即時對話介面
- **WebSocket 通訊**: 即時雙向通訊
- **美觀 UI**: 基於 Bootstrap 的現代化界面
- **對話歷史**: 保存完整的面試對話記錄
- **響應式設計**: 支援桌面和移動設備

## 🏗️ 技術架構

```
📁 interviewer-agent/
├── 📁 app/                    # FastAPI 應用
│   ├── main.py               # 主應用入口
│   ├── config.py             # 配置管理
│   └── 📁 api/               # API 路由
│       ├── speech.py         # 語音處理 API
│       ├── llm.py           # LLM 處理 API
│       └── scraper.py       # 網站抓取 API
├── 📁 core/                  # 核心功能模組
│   ├── 📁 speech/           # 語音處理
│   ├── 📁 llm/              # LLM 整合
│   ├── 📁 scraper/          # 網站抓取
│   └── 📁 utils/            # 工具函數
├── 📁 ui/                   # 前端界面
│   ├── 📁 static/           # 靜態資源
│   └── 📁 templates/        # HTML 模板
└── 📁 tests/                # 測試文件
```

## 🚀 快速開始

### 1. 環境需求

- Python 3.9+
- Chrome/Chromium 瀏覽器 (用於網站抓取)
- 麥克風設備 (用於語音輸入)

### 2. 安裝依賴

```bash
# 克隆專案
git clone <repository-url>
cd interviewer-agent

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 3. 環境配置

複製並編輯環境變數文件：

```bash
cp env_example.txt .env
```

編輯 `.env` 文件，設定必要的 API 金鑰：

```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI API (用於 Whisper STT)
OPENAI_API_KEY=your_openai_api_key_here

# 其他配置...
```

### 4. 啟動應用

```bash
# 開發模式
python app/main.py

# 或使用 uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. 訪問應用

打開瀏覽器，訪問 `http://localhost:8000`

## 📖 使用指南

### 開始面試

1. **選擇面試類型**: 在控制面板中選擇技術面試、行為面試或系統設計
2. **設定 LeetCode URL**: 如果是技術面試，貼上 LeetCode 題目連結
3. **點擊開始面試**: 系統會自動生成歡迎訊息
4. **開始對話**: 使用語音錄音或文字輸入與 AI 面試官對話

### 語音功能

- **錄音**: 點擊「🎤 開始錄音」按鈕開始語音輸入
- **音量控制**: 使用音量滑桿調整語音播放音量
- **自動轉錄**: 錄音結束後自動轉換為文字並發送給 AI

### 程式碼抓取

- **手動抓取**: 點擊「手動抓取程式碼」立即獲取當前程式碼
- **自動抓取**: 設定抓取間隔，自動定期獲取程式碼變化
- **即時分析**: AI 會自動分析程式碼並提供建議

## 🔧 配置選項

### 語音設定

```bash
# Speech-to-Text
STT_SERVICE=whisper          # whisper, google
STT_LANGUAGE=zh-TW          # 語言代碼

# Text-to-Speech  
TTS_SERVICE=edge            # edge, gtts, openai
TTS_VOICE=zh-TW-HsiaoChenNeural  # 語音模型
TTS_SPEED=1.0               # 語音速度
```

### 抓取設定

```bash
# 抓取間隔 (秒)
SCRAPING_INTERVAL=10

# 瀏覽器設定
SELENIUM_DRIVER=chrome
HEADLESS_MODE=true
```

### 面試設定

```bash
# 預設面試類型
DEFAULT_INTERVIEW_TYPE=technical

# 對話歷史長度
MAX_CONVERSATION_HISTORY=50

# 面試時間限制 (秒)
INTERVIEW_TIMEOUT=3600
```

## 🔌 API 文檔

啟動應用後，可以訪問自動生成的 API 文檔：

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 主要 API 端點

#### 語音處理
- `POST /api/speech/stt` - 語音轉文字
- `POST /api/speech/tts` - 文字轉語音
- `GET /api/speech/stt/status` - STT 服務狀態

#### LLM 處理
- `POST /api/llm/chat` - 與 AI 面試官對話
- `POST /api/llm/analyze-code` - 程式碼分析
- `POST /api/llm/start-interview` - 開始面試
- `GET /api/llm/interview-types` - 獲取面試類型

#### 網站抓取
- `POST /api/scraper/manual` - 手動抓取
- `POST /api/scraper/auto/start` - 開始自動抓取
- `POST /api/scraper/auto/stop` - 停止自動抓取
- `GET /api/scraper/platforms` - 支援的平台

## 🧪 測試

運行測試套件：

```bash
# 運行所有測試
pytest

# 運行特定測試
pytest tests/test_speech.py
pytest tests/test_llm.py
pytest tests/test_scraper.py

# 產生測試覆蓋率報告
pytest --cov=app --cov-report=html
```

## 🐳 Docker 部署

### 使用 Docker Compose

```bash
# 構建並啟動
docker-compose up --build

# 背景運行
docker-compose up -d
```

### 單獨使用 Docker

```bash
# 構建映像
docker build -t interviewer-agent .

# 運行容器
docker run -p 8000:8000 --env-file .env interviewer-agent
```

## 🤝 貢獻指南

1. **Fork 專案**
2. **創建功能分支**: `git checkout -b feature/新功能`
3. **提交變更**: `git commit -am 'Add: 新增某功能'`
4. **推送分支**: `git push origin feature/新功能`
5. **建立 Pull Request**

### 開發規範

- 使用 Black 進行程式碼格式化: `black .`
- 使用 flake8 進行程式碼檢查: `flake8 .`
- 新增功能必須包含測試
- 提交訊息使用英文，遵循 Conventional Commits

## 📝 更新日誌

### v1.0.0 (2024-01-XX)
- ✅ 基礎專案架構
- ✅ FastAPI 後端服務
- ✅ 語音處理功能 (STT/TTS)
- ✅ Gemini LLM 整合
- ✅ LeetCode 抓取功能
- ✅ WebSocket 即時通訊
- ✅ 響應式 Web UI

## 🔒 安全注意事項

- **API 金鑰安全**: 確保 `.env` 文件不被提交到版本控制
- **語音資料**: 語音資料僅在本地處理，不會上傳到伺服器
- **網站抓取**: 遵守目標網站的 robots.txt 和使用條款
- **隱私保護**: 面試資料僅在本地儲存

## 📄 授權

本專案使用 [MIT License](LICENSE)。

## 🙏 致謝

- [Google Gemini](https://deepmind.google/technologies/gemini/) - 提供強大的 LLM 服務
- [OpenAI Whisper](https://openai.com/research/whisper) - 語音識別技術
- [FastAPI](https://fastapi.tiangolo.com/) - 現代 Python Web 框架
- [Bootstrap](https://getbootstrap.com/) - 前端 UI 框架

## 📞 聯絡方式

如有問題或建議，請通過以下方式聯絡：

- 📧 Email: [your-email@example.com]
- 💬 GitHub Issues: [專案 Issues 頁面]
- 🐦 Twitter: [@your-twitter]

---

**注意**: 本工具僅供學習和練習使用，實際面試結果可能因人而異。請將其作為面試準備的輔助工具，而非唯一依據。 
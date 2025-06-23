# AI 面試模擬工具 - 專案規劃

## 📋 專案概述
基於 Gemini LLM 的智能面試工具，支援語音對話、程式碼實時抓取與分析。

## 🏗️ 專案架構

```
interviewer-agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 主應用
│   ├── config.py              # 配置設定
│   └── api/
│       ├── __init__.py
│       ├── speech.py          # 語音處理 API
│       ├── llm.py             # LLM 處理 API
│       └── scraper.py         # 網站抓取 API
├── core/
│   ├── __init__.py
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── stt.py             # Speech-to-Text
│   │   └── tts.py             # Text-to-Speech
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── gemini_client.py   # Gemini API 客戶端
│   │   └── interviewer.py     # 面試官邏輯
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── leetcode.py        # LeetCode 抓取
│   │   └── base_scraper.py    # 基礎抓取類
│   └── utils/
│       ├── __init__.py
│       ├── audio_utils.py     # 音頻工具
│       └── text_utils.py      # 文字處理工具
├── ui/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── audio/
│   ├── templates/
│   │   └── index.html         # 主界面
│   └── components/
│       ├── audio_recorder.js  # 音頻錄製組件
│       ├── chat_interface.js  # 聊天界面組件
│       └── code_viewer.js     # 程式碼檢視組件
├── tests/
│   ├── __init__.py
│   ├── test_speech.py
│   ├── test_llm.py
│   └── test_scraper.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🔧 技術堆棧

### 後端
- **Framework**: FastAPI (高效能、WebSocket支援)
- **LLM**: Google Gemini API
- **語音處理**: 
  - STT: OpenAI Whisper / Google Speech-to-Text
  - TTS: Google Text-to-Speech / ElevenLabs
- **網站抓取**: Selenium / Playwright
- **任務調度**: APScheduler
- **WebSocket**: 即時通訊

### 前端
- **基礎**: HTML5 + CSS3 + JavaScript
- **音頻**: Web Audio API
- **UI框架**: Bootstrap 或 Tailwind CSS
- **即時通訊**: WebSocket

### 部署
- **容器化**: Docker + Docker Compose
- **環境配置**: .env 文件管理

## 📝 功能模組詳細規劃

### 1. 語音處理模組
#### STT (Speech-to-Text)
- 支援即時語音識別
- 多語言支援 (中文/英文)
- 降噪處理
- 支援麥克風和系統音頻輸入

#### TTS (Text-to-Speech)
- 自然語音合成
- 可調整語速、音調
- 支援多種聲音模型
- 即時播放功能

### 2. LLM 整合模組
#### Gemini 客戶端
- API 金鑰管理
- 請求限制與重試機制
- 上下文管理
- 結果格式化

#### 面試官角色
- 多種面試類型 (技術/行為/系統設計)
- 動態問題生成
- 程式碼分析與建議
- 面試評估與回饋

### 3. 網站抓取模組
#### LeetCode 抓取器
- 程式碼內容實時獲取
- 執行結果監控
- 測試案例分析
- 提交歷史追蹤

#### 通用抓取器
- 可擴展其他程式平台
- 反爬蟲機制處理
- 內容變化檢測
- 快取機制

### 4. 前端介面
#### 主要功能
- 語音錄製與播放
- 即時對話顯示
- 程式碼即時檢視
- 面試設定面板
- 歷史記錄查看

#### 互動設計
- 一鍵開始/結束面試
- 手動觸發程式碼抓取
- 設定自動抓取間隔
- 音量控制與靜音

## 🚀 實作階段

### Phase 1: 基礎架構 (Week 1)
- [x] 專案結構建立
- [ ] FastAPI 基礎服務
- [ ] 環境配置管理
- [ ] 基礎 UI 框架

### Phase 2: 語音功能 (Week 2)
- [ ] STT 功能實作
- [ ] TTS 功能實作
- [ ] 音頻錄製與播放
- [ ] WebSocket 即時通訊

### Phase 3: LLM 整合 (Week 3)
- [ ] Gemini API 整合
- [ ] 面試官角色設計
- [ ] 對話邏輯實作
- [ ] 上下文管理

### Phase 4: 網站抓取 (Week 4)
- [ ] LeetCode 抓取器
- [ ] 定時/手動抓取
- [ ] 內容分析處理
- [ ] 抓取結果整合

### Phase 5: 整合測試 (Week 5)
- [ ] 功能整合測試
- [ ] 效能優化
- [ ] 錯誤處理完善
- [ ] 使用者體驗優化

### Phase 6: 部署優化 (Week 6)
- [ ] Docker 容器化
- [ ] 部署腳本
- [ ] 監控與日誌
- [ ] 文檔完善

## 🔒 安全與隱私
- API 金鑰安全管理
- 音頻資料本地處理
- 敏感資訊過濾
- 使用者隱私保護

## 📊 效能考量
- 音頻流處理優化
- LLM 回應快取
- 網站抓取頻率控制
- 資源使用監控

## 🧪 測試策略
- 單元測試覆蓋
- 整合測試
- 效能測試
- 使用者接受測試 
# AI 面試模擬器 - MVP版本

## 專案概述

這是一個簡化版的AI面試模擬工具，專注於核心功能的快速驗證。MVP版本將大幅簡化原有的複雜架構，專注於最基本的面試功能。

## 核心目標

- **快速驗證概念**: 在2-3週內完成可用的MVP版本
- **最小化複雜性**: 移除非必要功能，專注核心體驗
- **漸進式開發**: 建立可擴展的基礎架構

## MVP範圍

### ✅ 包含功能
- 基本的文字對話界面
- Gemini LLM 面試官
- 簡單的程式碼輸入框(手動輸入)
- 基礎的面試類型選擇

### ❌ 暫不包含
- 語音功能 (STT/TTS)
- 自動網站抓取
- 複雜的UI設計
- WebSocket 即時通訊
- 多用戶支援

## 技術架構(簡化版)

```
mvp-interviewer/
├── app.py              # 單一Flask應用
├── config.py           # 簡單配置
├── llm_client.py      # Gemini客戶端
├── templates/         # HTML模板
│   └── index.html     # 單頁面應用
├── static/           # 靜態文件
│   ├── style.css     # 基礎樣式
│   └── script.js     # 基礎JS
└── requirements.txt  # 最小依賴
```

## 功能計劃索引

詳細的功能規劃請參考以下文檔：

- [核心面試功能](features/core-interview-plan.md) - 基本的AI面試對話功能
- [程式碼分析功能](features/code-analysis-plan.md) - 簡單的程式碼輸入與分析
- [基礎UI界面](features/basic-ui-plan.md) - 最小可用界面

## 開發時程

- **第1週**: 核心面試功能
- **第2週**: 程式碼分析功能  
- **第3週**: 基礎UI整合與測試

## 成功指標

- 能夠進行基本的技術面試對話
- 能夠分析簡單的程式碼片段
- 具備可擴展到完整版本的架構基礎

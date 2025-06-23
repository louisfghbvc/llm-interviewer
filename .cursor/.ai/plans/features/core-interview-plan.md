# PRD: 核心面試功能

## 1. Product overview

### 1.1 Document title and version

- PRD: 核心面試功能
- Version: 1.0

### 1.2 Product summary

核心面試功能是MVP版本的主要模組，提供基於Gemini LLM的AI面試官對話能力。用戶可以通過文字輸入與AI面試官進行技術面試對話，AI面試官會根據面試類型提出相應問題並評估回答。

這個功能專注於最基本的面試體驗，為後續擴展功能建立堅實的基礎。

## 2. Goals

### 2.1 Business goals

- 快速驗證AI面試概念的可行性
- 建立可擴展的LLM整合基礎
- 在2週內完成核心功能開發
- 為完整版本奠定技術基礎

### 2.2 User goals

- 體驗AI面試官的對話能力
- 練習基本的面試問答
- 獲得AI面試官的即時回饋
- 準備真實的技術面試

### 2.3 Non-goals

- 語音功能整合
- 複雜的面試報告生成
- 多輪面試管理
- 用戶帳戶系統

## 3. User personas

### 3.1 Key user types

- 求職者 - 準備技術面試
- 開發者 - 測試AI面試工具

### 3.2 Basic persona details

- **技術求職者**: 希望練習程式設計面試的軟體工程師
- **MVP測試者**: 想要驗證AI面試工具概念的早期用戶

### 3.3 Role-based access

- **一般用戶**: 可以開始面試對話，選擇面試類型，與AI互動

## 4. Functional requirements

- **AI面試對話** (Priority: High)
  - 整合Gemini API進行自然語言對話
  - 支援技術面試、行為面試兩種基本類型
  - 維持對話上下文和面試狀態

- **面試類型選擇** (Priority: High)
  - 提供技術面試和行為面試選項
  - 根據選擇調整AI面試官的提問風格
  - 顯示當前面試類型狀態

- **基本回饋系統** (Priority: Medium)
  - AI面試官能夠對回答給出簡單評價
  - 提供改進建議
  - 記錄基本的對話歷史

## 5. User experience

### 5.1 Entry points & first-time user flow

用戶訪問網頁應用，立即看到簡潔的面試界面，可以選擇面試類型並開始對話。

### 5.2 Core experience

- **第1步: 選擇面試類型**: 用戶選擇技術面試或行為面試
  - 提供清楚的類型說明，讓用戶了解不同面試的特點
- **第2步: 開始面試**: AI面試官主動問候並開始提問
  - 自然友善的開場，讓用戶感到舒適
- **第3步: 對話互動**: 用戶輸入回答，AI給出回應和進一步問題
  - 流暢的對話體驗，AI能理解並回應用戶的回答

### 5.3 Advanced features & edge cases

- 處理無效或過短的回答
- 面試中途重新開始的功能
- 對話歷史的簡單查看

### 5.4 UI/UX highlights

- 簡潔直觀的聊天界面
- 清楚的面試類型指示
- 即時的對話顯示

## 6. Narrative

用戶打開網頁，選擇技術面試，AI面試官立即開始友善的對話："您好！我是您今天的技術面試官。讓我們從您的自我介紹開始吧。"用戶輸入回答後，AI會根據回答內容提出相關的技術問題，整個過程自然流暢，讓用戶獲得真實的面試練習體驗。

## 7. Success metrics

### 7.1 User-centric metrics

- 對話輪次平均數量 (目標: >5輪)
- 用戶完成面試的比例 (目標: >70%)
- AI回應的相關性評分

### 7.2 Business metrics

- 功能可用性 (目標: 99%正常運行)
- 平均開發完成時間 (目標: <2週)

### 7.3 Technical metrics

- API回應時間 (目標: <3秒)
- 錯誤率 (目標: <5%)

## 8. Technical considerations

### 8.1 Integration points

- Google Gemini API整合
- Flask後端框架
- 簡單的前端JavaScript

### 8.2 Data storage & privacy

- 僅在記憶體中暫存對話
- 不儲存個人資料
- API金鑰安全管理

### 8.3 Scalability & performance

- 單用戶同時使用
- 基本的錯誤處理
- API速率限制考量

### 8.4 Potential challenges

- Gemini API的回應品質控制
- 中文對話的自然度
- 面試上下文的維持

## 9. Milestones & sequencing

### 9.1 Project estimate

- Small: 1-2週

### 9.2 Team size & composition

- Small Team: 1人 (全端開發)

### 9.3 Suggested phases

- **Phase 1**: Gemini API整合與基本對話 (1週)
  - Key deliverables: 能夠進行基本對話的後端
- **Phase 2**: 面試類型與前端整合 (1週)
  - Key deliverables: 完整的MVP面試功能

## 10. User stories

### 10.1 開始技術面試

- **ID**: US-001
- **Description**: 身為求職者，我想要開始一場技術面試，以便練習程式設計相關問題。
- **Acceptance Criteria**:
  - 我可以選擇"技術面試"選項
  - AI面試官會以技術面試的方式開始對話
  - AI會提出程式設計相關的問題

### 10.2 進行對話互動

- **ID**: US-002
- **Description**: 身為用戶，我想要與AI面試官進行自然對話，以便獲得真實的面試體驗。
- **Acceptance Criteria**:
  - 我可以在文字框輸入回答
  - AI會理解我的回答並給出相關回應
  - 對話歷史會顯示在頁面上
  - AI會根據我的回答提出後續問題

### 10.3 獲得基本回饋

- **ID**: US-003
- **Description**: 身為求職者，我想要獲得AI面試官的回饋，以便改進我的面試表現。
- **Acceptance Criteria**:
  - AI會對我的技術回答給出評價
  - AI會提供改進建議
  - 回饋內容具體且有用

### 10.4 選擇面試類型

- **ID**: US-004
- **Description**: 身為用戶，我想要選擇不同的面試類型，以便針對性地練習。
- **Acceptance Criteria**:
  - 我可以在技術面試和行為面試間選擇
  - 不同類型的面試會有不同的提問風格
  - 介面會顯示當前的面試類型

### 10.5 重新開始面試

- **ID**: US-005
- **Description**: 身為用戶，我想要能夠重新開始面試，以便重新練習。
- **Acceptance Criteria**:
  - 我可以點擊按鈕重新開始面試
  - 對話歷史會被清空
  - AI會重新開始問候和提問
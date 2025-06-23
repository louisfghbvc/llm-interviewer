# PRD: 程式碼分析功能

## 1. Product overview

### 1.1 Document title and version

- PRD: 程式碼分析功能
- Version: 1.0

### 1.2 Product summary

程式碼分析功能允許用戶手動輸入程式碼片段，AI面試官會分析程式碼的正確性、效率和風格，並提供改進建議。這是MVP版本中的重要功能，讓技術面試更加具體和實用。

功能採用簡單的文字輸入方式，避免複雜的網站抓取，專注於AI分析能力的驗證。

## 2. Goals

### 2.1 Business goals

- 展示AI程式碼分析的能力
- 為技術面試提供具體的程式碼評估
- 建立程式碼分析的基礎架構
- 驗證AI對程式碼理解的準確性

### 2.2 User goals

- 獲得程式碼的專業分析和建議
- 學習更好的程式設計實作方法
- 準備程式設計面試的編碼環節
- 理解程式碼的優缺點

### 2.3 Non-goals

- 自動執行程式碼
- 支援複雜的專案結構
- 即時程式碼編輯器
- 版本控制整合

## 3. User personas

### 3.1 Key user types

- 程式設計面試候選人
- 學習程式設計的開發者

### 3.2 Basic persona details

- **面試準備者**: 想要練習程式設計題目並獲得回饋的求職者
- **程式學習者**: 希望改進程式碼品質的初學者

### 3.3 Role-based access

- **一般用戶**: 可以輸入程式碼，獲得分析結果，查看建議

## 4. Functional requirements

- **程式碼輸入界面** (Priority: High)
  - 提供大型文字輸入框供用戶貼上程式碼
  - 支援多種程式語言(Python, JavaScript, Java等)
  - 保持程式碼格式和縮排

- **AI程式碼分析** (Priority: High)
  - 分析程式碼邏輯正確性
  - 評估時間和空間複雜度
  - 檢查程式碼風格和最佳實務
  - 提供具體的改進建議

- **分析結果顯示** (Priority: High)
  - 清楚顯示分析結果
  - 突出程式碼中的問題點
  - 提供改進前後的對比建議

- **語言選擇** (Priority: Medium)
  - 用戶可以選擇程式碼語言
  - AI根據語言調整分析方式
  - 支援常見的程式語言

## 5. User experience

### 5.1 Entry points & first-time user flow

用戶在面試過程中可以選擇"分析我的程式碼"選項，然後進入程式碼輸入界面。

### 5.2 Core experience

- **第1步: 選擇程式語言**: 用戶選擇程式碼的語言類型
  - 提供清楚的語言選項，幫助AI更好地分析
- **第2步: 輸入程式碼**: 用戶在文字框中貼上或輸入程式碼
  - 大型輸入框，支援程式碼格式化
- **第3步: 獲得分析**: AI分析程式碼並提供詳細回饋
  - 結構化的分析結果，易於理解

### 5.3 Advanced features & edge cases

- 處理不完整的程式碼片段
- 檢測無效或錯誤的程式碼
- 支援偽程式碼分析

### 5.4 UI/UX highlights

- 程式碼語法高亮顯示
- 清楚的分析結果分類
- 互動式的改進建議

## 6. Narrative

用戶在技術面試中被問到一個演算法問題，寫出解答後，選擇"讓AI分析我的程式碼"。用戶選擇Python語言，貼上自己的程式碼，AI立即分析並回應："您的解決方案邏輯正確，時間複雜度為O(n²)。我建議您可以使用雜湊表來優化到O(n)，這裡是具體的改進方法..."

## 7. Success metrics

### 7.1 User-centric metrics

- 程式碼分析準確率 (目標: >85%)
- 用戶對建議的有用性評分
- 程式碼輸入完成率

### 7.2 Business metrics

- 功能使用頻率
- 分析功能的可用性

### 7.3 Technical metrics

- 程式碼分析回應時間 (目標: <5秒)
- API調用成功率 (目標: >95%)

## 8. Technical considerations

### 8.1 Integration points

- 與核心面試功能整合
- Gemini API的程式碼分析能力
- 前端程式碼顯示元件

### 8.2 Data storage & privacy

- 不永久儲存用戶程式碼
- 保護程式碼隱私
- 僅用於當次分析

### 8.3 Scalability & performance

- 處理大型程式碼片段
- 優化API請求效率
- 錯誤處理機制

### 8.4 Potential challenges

- AI對複雜程式碼的理解限制
- 不同程式語言的分析品質差異
- 程式碼格式保持

## 9. Milestones & sequencing

### 9.1 Project estimate

- Small: 1週

### 9.2 Team size & composition

- Small Team: 1人 (全端開發)

### 9.3 Suggested phases

- **Phase 1**: 程式碼輸入界面與基本分析 (0.5週)
  - Key deliverables: 程式碼輸入和簡單分析
- **Phase 2**: 進階分析功能與UI優化 (0.5週)
  - Key deliverables: 完整的程式碼分析功能

## 10. User stories

### 10.1 輸入程式碼進行分析

- **ID**: US-006
- **Description**: 身為程式設計面試者，我想要輸入我的程式碼讓AI分析，以便獲得專業的回饋。
- **Acceptance Criteria**:
  - 我可以選擇程式語言類型
  - 我可以在文字框中輸入或貼上程式碼
  - 程式碼格式會被保持
  - 我可以提交程式碼進行分析

### 10.2 獲得程式碼分析結果

- **ID**: US-007
- **Description**: 身為用戶，我想要獲得AI對我程式碼的詳細分析，以便了解優缺點。
- **Acceptance Criteria**:
  - AI會分析程式碼的邏輯正確性
  - AI會評估時間和空間複雜度
  - AI會指出程式碼風格問題
  - 分析結果清楚易懂

### 10.3 獲得改進建議

- **ID**: US-008
- **Description**: 身為學習者，我想要獲得具體的程式碼改進建議，以便提升我的程式設計能力。
- **Acceptance Criteria**:
  - AI會提供具體的改進建議
  - 建議包含程式碼範例或說明
  - 建議針對效能、可讀性等不同面向
  - 建議容易理解和實施

### 10.4 支援多種程式語言

- **ID**: US-009
- **Description**: 身為開發者，我想要分析不同程式語言的程式碼，以便在各種技術面試中使用。
- **Acceptance Criteria**:
  - 支援Python、JavaScript、Java等常見語言
  - 不同語言有相應的分析特點
  - 語言選擇界面清楚直觀
  - AI能正確識別和分析不同語言

### 10.5 在面試中整合程式碼分析

- **ID**: US-010
- **Description**: 身為面試參與者，我想要在面試對話中無縫使用程式碼分析功能，以便獲得連貫的面試體驗。
- **Acceptance Criteria**:
  - 我可以在面試對話中觸發程式碼分析
  - 分析結果會整合到面試對話中
  - AI面試官會根據程式碼分析調整後續問題
  - 整個流程自然流暢
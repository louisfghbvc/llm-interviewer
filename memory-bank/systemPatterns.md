# 系統架構與設計模式

## 整體架構設計

### 系統架構圖
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   External      │
│   (Web UI)      │◄──►│   Server        │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                    ┌─────────────────┐      ┌─────────────────┐
                    │   Core Logic    │      │   Google        │
                    │   Components    │      │   Gemini API    │
                    └─────────────────┘      └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Data Layer    │
                    │   (In-Memory)   │
                    └─────────────────┘
```

### 核心組件關係

#### 1. Flask Application (main.py)
- **角色**: API 閘道和請求路由
- **職責**: HTTP 請求處理、錯誤管理、CORS 設定
- **依賴**: InterviewManager, CodeHandler, LLMClient

#### 2. Interview Manager (interview_manager.py)
- **角色**: 面試流程控制中心
- **職責**: 會話管理、狀態追蹤、評分邏輯
- **依賴**: LLMClient
- **設計模式**: 狀態機模式

#### 3. LLM Client (llm_client.py)
- **角色**: AI 服務抽象層
- **職責**: Gemini API 整合、對話管理、重試機制
- **設計模式**: 適配器模式、單例模式

#### 4. Code Handler (code_handler.py)
- **角色**: 程式碼分析引擎
- **職責**: 語法驗證、安全檢查、複雜度分析
- **設計模式**: 策略模式、工廠模式

## 關鍵技術決策

### 1. 架構決策

#### Flask vs FastAPI
**選擇**: Flask
**理由**: 
- 簡單直接，符合 MVP 快速開發需求
- 豐富的生態系統和文檔
- 團隊熟悉度高

#### 同步 vs 異步
**選擇**: 同步架構
**理由**:
- MVP 版本不需要高併發處理
- 減少複雜度，專注核心功能
- 後續可升級為異步

### 2. AI 整合決策

#### LLM 選擇: Gemini vs OpenAI
**選擇**: Google Gemini
**理由**:
- 免費額度較高
- 多模態支援（未來擴展）
- Google Cloud 生態整合

#### 對話管理策略
**選擇**: Session-based 會話管理
**模式**: 
```python
sessions[session_id] = {
    'history': [],
    'state': InterviewState,
    'metrics': InterviewMetrics
}
```

### 3. 程式碼分析決策

#### 語法驗證策略
**多層驗證方法**:
1. **第一層**: 原生編譯器驗證 (clang++, python ast)
2. **第二層**: 基礎語法規則檢查
3. **第三層**: 自定義安全規則

#### 支援語言優先級
1. **Python**: AST 解析 + 語法檢查
2. **C++**: clang++ 編譯器驗證
3. **JavaScript**: 基礎語法檢查
4. **其他**: 通用模式匹配

### 4. 資料管理決策

#### 持久化策略
**選擇**: 記憶體儲存 (MVP)
**理由**:
- 簡化部署和開發
- 無需資料庫設定
- 符合單用戶 MVP 需求

#### 會話生命周期
```python
session_lifecycle = {
    'creation': 'on_demand',
    'duration': 'unlimited',
    'cleanup': 'manual_or_restart'
}
```

## 設計模式應用

### 1. 狀態機模式 (Interview Manager)
```python
class InterviewState(Enum):
    INIT = "init"
    INTRODUCTION = "introduction"  
    QUESTIONING = "questioning"
    CODE_REVIEW = "code_review"
    EVALUATION = "evaluation"
    COMPLETED = "completed"
```

### 2. 策略模式 (Code Validation)
```python
class CodeHandler:
    def validate_code(self, code, language):
        if language == 'python':
            return self._validate_python_syntax(code)
        elif language == 'cpp':
            return self._validate_cpp_syntax_with_clang(code)
```

### 3. 建造者模式 (Response Construction)
```python
response_builder = {
    'success': bool,
    'data': dict,
    'errors': list,
    'metadata': dict
}
```

## 擴展性考量

### 1. 模組化設計
- 每個核心組件獨立可測試
- 清晰的介面定義
- 最小依賴耦合

### 2. 插件式架構準備
```python
# 未來可擴展為
class CodeValidator:
    def register_language_handler(self, language, handler):
        self.handlers[language] = handler
```

### 3. API 版本控制
- RESTful URL 設計
- 統一錯誤處理
- 標準化回應格式

## 效能最佳化

### 1. 快取策略
- LLM 回應快取（未來）
- 程式碼驗證結果快取
- 會話狀態快取

### 2. 資源管理
- 連線池管理
- 超時控制
- 記憶體清理

### 3. 監控點設計
- API 回應時間
- LLM 調用延遲
- 錯誤率統計 
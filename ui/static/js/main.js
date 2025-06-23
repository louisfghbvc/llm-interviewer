// Main JavaScript for AI Interviewer Agent
class InterviewerApp {
    constructor() {
        this.isInterviewActive = false;
        this.isRecording = false;
        this.isAutoScraping = false;
        this.websocket = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.checkServiceStatus();
    }
    
    setupEventListeners() {
        // Interview controls
        document.getElementById('start-interview').addEventListener('click', () => this.startInterview());
        document.getElementById('stop-interview').addEventListener('click', () => this.stopInterview());
        
        // Audio controls
        document.getElementById('start-recording').addEventListener('click', () => this.startRecording());
        document.getElementById('stop-recording').addEventListener('click', () => this.stopRecording());
        
        // Scraping controls
        document.getElementById('manual-scrape').addEventListener('click', () => this.manualScrape());
        document.getElementById('toggle-auto-scrape').addEventListener('click', () => this.toggleAutoScrape());
        
        // Chat controls
        document.getElementById('send-message').addEventListener('click', () => this.sendMessage());
        document.getElementById('message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Volume control
        document.getElementById('volume-control').addEventListener('input', (e) => {
            this.setVolume(e.target.value / 100);
        });
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        
        this.websocket.onopen = () => {
            console.log('WebSocket connected');
            this.showStatus('WebSocket 已連接', 'success');
        };
        
        this.websocket.onmessage = (event) => {
            this.handleWebSocketMessage(event.data);
        };
        
        this.websocket.onclose = () => {
            console.log('WebSocket disconnected');
            this.showStatus('WebSocket 連接已斷開', 'warning');
            // Auto-reconnect after 3 seconds
            setTimeout(() => this.connectWebSocket(), 3000);
        };
        
        this.websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showStatus('WebSocket 連接錯誤', 'error');
        };
    }
    
    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            
            if (message.type === 'scrape_result') {
                this.updateCodeDisplay(message.data);
            } else if (message.type === 'chat_response') {
                this.addChatMessage(message.content, 'assistant');
                this.playTTS(message.content);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }
    
    async startInterview() {
        try {
            const interviewType = document.getElementById('interview-type').value;
            
            const response = await fetch('/api/llm/start-interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    interview_type: interviewType,
                    candidate_name: '面試者',
                    position: '軟體工程師'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isInterviewActive = true;
                this.updateInterviewUI(true);
                this.addChatMessage(result.welcome_message, 'assistant');
                this.playTTS(result.welcome_message);
                this.showStatus('面試已開始', 'success');
            }
        } catch (error) {
            console.error('Error starting interview:', error);
            this.showStatus('無法開始面試', 'error');
        }
    }
    
    async stopInterview() {
        if (this.isInterviewActive) {
            this.isInterviewActive = false;
            this.updateInterviewUI(false);
            this.showStatus('面試已結束', 'info');
        }
    }
    
    async startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });
            
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                this.processAudioRecording();
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            this.updateRecordingUI(true);
            
        } catch (error) {
            console.error('Error starting recording:', error);
            this.showStatus('無法開始錄音', 'error');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.updateRecordingUI(false);
            
            // Stop all tracks
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
    }
    
    async processAudioRecording() {
        try {
            const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.wav');
            
            this.showStatus('正在處理語音...', 'info');
            
            const response = await fetch('/api/speech/stt', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addChatMessage(result.text, 'user');
                await this.sendChatMessage(result.text);
            }
        } catch (error) {
            console.error('Error processing audio:', error);
            this.showStatus('語音處理失敗', 'error');
        }
    }
    
    async manualScrape() {
        try {
            const url = document.getElementById('leetcode-url').value;
            if (!url) {
                this.showStatus('請輸入 LeetCode URL', 'warning');
                return;
            }
            
            this.showStatus('正在抓取程式碼...', 'info');
            
            const response = await fetch('/api/scraper/manual', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: url,
                    platform: 'leetcode'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.updateCodeDisplay(result);
                this.showStatus('程式碼抓取成功', 'success');
            }
        } catch (error) {
            console.error('Error scraping code:', error);
            this.showStatus('程式碼抓取失敗', 'error');
        }
    }
    
    async toggleAutoScrape() {
        const button = document.getElementById('toggle-auto-scrape');
        
        if (!this.isAutoScraping) {
            // Start auto-scraping
            const url = document.getElementById('leetcode-url').value;
            const interval = parseInt(document.getElementById('scraping-interval').value);
            
            if (!url) {
                this.showStatus('請輸入 LeetCode URL', 'warning');
                return;
            }
            
            try {
                const response = await fetch('/api/scraper/auto/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        url: url,
                        interval: interval,
                        platform: 'leetcode'
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    this.isAutoScraping = true;
                    button.textContent = '停止自動抓取';
                    button.className = 'btn btn-outline-danger';
                    this.showStatus('自動抓取已啟動', 'success');
                }
            } catch (error) {
                console.error('Error starting auto-scrape:', error);
                this.showStatus('無法啟動自動抓取', 'error');
            }
        } else {
            // Stop auto-scraping
            try {
                await fetch('/api/scraper/auto/stop', { method: 'POST' });
                this.isAutoScraping = false;
                button.textContent = '開啟自動抓取';
                button.className = 'btn btn-outline-warning';
                this.showStatus('自動抓取已停止', 'info');
            } catch (error) {
                console.error('Error stopping auto-scrape:', error);
            }
        }
    }
    
    async sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (!message) return;
        
        input.value = '';
        this.addChatMessage(message, 'user');
        
        await this.sendChatMessage(message);
    }
    
    async sendChatMessage(message) {
        try {
            const interviewType = document.getElementById('interview-type').value;
            
            const response = await fetch('/api/llm/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    interview_type: interviewType,
                    context: this.getCurrentContext()
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.addChatMessage(result.response, 'assistant');
                await this.playTTS(result.response);
            }
        } catch (error) {
            console.error('Error sending chat message:', error);
            this.showStatus('無法發送訊息', 'error');
        }
    }
    
    async playTTS(text) {
        try {
            const response = await fetch('/api/speech/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            if (response.ok) {
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                const volume = document.getElementById('volume-control').value / 100;
                audio.volume = volume;
                
                audio.play();
                
                audio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                };
            }
        } catch (error) {
            console.error('Error playing TTS:', error);
        }
    }
    
    updateCodeDisplay(data) {
        const codeDisplay = document.getElementById('code-display');
        const lastUpdate = document.getElementById('last-update');
        
        if (data.code) {
            codeDisplay.innerHTML = `<pre><code>${this.escapeHtml(data.code)}</code></pre>`;
        }
        
        lastUpdate.textContent = new Date().toLocaleTimeString();
    }
    
    addChatMessage(content, role) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role} fade-in`;
        
        const timestamp = new Date().toLocaleTimeString();
        messageDiv.innerHTML = `
            <div>${this.escapeHtml(content)}</div>
            <div class="timestamp">${timestamp}</div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    updateInterviewUI(active) {
        document.getElementById('start-interview').disabled = active;
        document.getElementById('stop-interview').disabled = !active;
        document.getElementById('message-input').disabled = !active;
        document.getElementById('send-message').disabled = !active;
    }
    
    updateRecordingUI(recording) {
        const startBtn = document.getElementById('start-recording');
        const stopBtn = document.getElementById('stop-recording');
        
        startBtn.disabled = recording;
        stopBtn.disabled = !recording;
        
        if (recording) {
            startBtn.className = 'btn btn-recording';
            startBtn.innerHTML = '🎤 錄音中...';
        } else {
            startBtn.className = 'btn btn-outline-success';
            startBtn.innerHTML = '🎤 開始錄音';
        }
    }
    
    setVolume(volume) {
        // Set volume for all audio elements
        const audioElements = document.querySelectorAll('audio');
        audioElements.forEach(audio => {
            audio.volume = volume;
        });
    }
    
    getCurrentContext() {
        const codeDisplay = document.getElementById('code-display');
        const code = codeDisplay.textContent;
        
        return {
            current_code: code,
            timestamp: new Date().toISOString()
        };
    }
    
    async checkServiceStatus() {
        try {
            const responses = await Promise.all([
                fetch('/api/speech/stt/status'),
                fetch('/api/speech/tts/status'),
                fetch('/api/llm/status'),
                fetch('/api/scraper/status')
            ]);
            
            const [sttStatus, ttsStatus, llmStatus, scraperStatus] = await Promise.all(
                responses.map(r => r.json())
            );
            
            console.log('Service status:', { sttStatus, ttsStatus, llmStatus, scraperStatus });
        } catch (error) {
            console.error('Error checking service status:', error);
        }
    }
    
    showStatus(message, type) {
        // Create a toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} fade-in`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.interviewerApp = new InterviewerApp();
}); 
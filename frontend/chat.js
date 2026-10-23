// frontend/chat.js
import { sendMessage } from './api.js';

const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');

let chatHistory = [];
let onMessageProcessedCallback = null;

function appendMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleSend() {
    const text = messageInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    messageInput.value = '';
    
    messageInput.disabled = true;
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';

    try {
        const response = await sendMessage(text, chatHistory);
        
        appendMessage('assistant', response.reply);
        
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'assistant', content: response.reply });
        
        if (onMessageProcessedCallback) {
            onMessageProcessedCallback();
        }
    } catch (error) {
        appendMessage('assistant', `Error: ${error.message}`);
    } finally {
        messageInput.disabled = false;
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
        messageInput.focus();
    }
}

export function initChat(onMessageProcessed) {
    onMessageProcessedCallback = onMessageProcessed;
    
    sendBtn.addEventListener('click', handleSend);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
    
    appendMessage('assistant', 'Hello John! I am ClinicPilot AI. How can I help you today? You can ask me about our doctors, treatments, or book an appointment.');
}
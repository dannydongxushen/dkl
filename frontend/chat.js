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
    sendBtn.textContent = 'Sending...';

    const loadingDiv = document.createElement('div');
    loadingDiv.className = `message assistant`;
    loadingDiv.style.color = '#64748b';
    loadingDiv.textContent = 'Analyzing intent...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    let stepTimeouts = [];
    
    stepTimeouts.push(setTimeout(() => {
        loadingDiv.textContent = 'Retrieving information...';
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 500));

    stepTimeouts.push(setTimeout(() => {
        loadingDiv.textContent = 'Thinking...';
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 1000));

    stepTimeouts.push(setTimeout(() => {
        loadingDiv.textContent = 'Generating response...';
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 2000));

    try {
        const response = await sendMessage(text, chatHistory);
        
        stepTimeouts.forEach(clearTimeout);
        chatBox.removeChild(loadingDiv);
        
        appendMessage('assistant', response.reply);
        
        chatHistory.push({ role: 'user', content: text });
        chatHistory.push({ role: 'assistant', content: response.reply });
        
        if (onMessageProcessedCallback) {
            onMessageProcessedCallback();
        }
    } catch (error) {
        stepTimeouts.forEach(clearTimeout);
        chatBox.removeChild(loadingDiv);
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
    
    appendMessage('assistant', 'Hello John! I am ClinicPilot AI. How can I help you today?\n\nHere are a few things you can try:\n1. "I have a peanut allergy, can I get a flu shot?"\n2. "What are my upcoming appointments?"\n3. "I want to book a general checkup for next Monday at 10 AM."');
}
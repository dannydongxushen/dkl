// frontend/api.js
const API_BASE = '/api';

export async function sendMessage(message, history) {
    const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            patient_id: 'P001',
            history: history
        })
    });
    
    if (!response.ok) {
        throw new Error(`Chat API error: ${response.status}`);
    }
    
    return await response.json();
}

export async function fetchBookings() {
    const response = await fetch(`${API_BASE}/bookings?patient_id=P001`);
    
    if (!response.ok) {
        throw new Error(`Bookings API error: ${response.status}`);
    }
    
    return await response.json();
}
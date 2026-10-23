import { initChat } from './chat.js';
import { initBookings, loadBookings } from './bookings.js';

function updateClock() {
    const now = new Date();
    const options = { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit', 
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    };
    // 格式类似: Fri, Oct 23, 17:45:30
    const timeString = now.toLocaleDateString('en-US', options).replace(',', '');
    const datetimeEl = document.getElementById('current-datetime');
    if (datetimeEl) {
        datetimeEl.textContent = timeString;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // 立即执行一次，避免初始时的 Loading...
    updateClock();
    // 每秒刷新一次
    setInterval(updateClock, 1000);

    initBookings();
    // 将 loadBookings 作为回调，AI 回复后刷新表格
    initChat(loadBookings);
});
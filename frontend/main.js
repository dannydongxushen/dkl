// frontend/main.js
import { initChat } from './chat.js';
import { initBookings, loadBookings } from './bookings.js';

document.addEventListener('DOMContentLoaded', () => {
    initBookings();
    initChat(loadBookings);
});
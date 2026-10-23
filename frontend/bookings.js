// frontend/bookings.js
import { fetchBookings } from './api.js';

const bookingsBody = document.getElementById('bookings-body');
const refreshBtn = document.getElementById('refresh-btn');

export async function loadBookings() {
    try {
        const data = await fetchBookings();
        bookingsBody.innerHTML = '';
        
        if (!data.bookings || data.bookings.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td colspan="5" style="text-align: center;">No bookings found.</td>`;
            bookingsBody.appendChild(tr);
            return;
        }

        data.bookings.forEach(booking => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${booking.booking_date}</td>
                <td>${booking.booking_time}</td>
                <td>${booking.doctor_name}</td>
                <td>${booking.treatment_name}</td>
                <td><span style="color: ${booking.status === 'Confirmed' ? 'green' : 'gray'};">${booking.status}</span></td>
            `;
            bookingsBody.appendChild(tr);
        });
    } catch (error) {
        console.error('Failed to load bookings:', error);
        bookingsBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: red;">Error loading bookings.</td></tr>`;
    }
}

export function initBookings() {
    refreshBtn.addEventListener('click', loadBookings);
    loadBookings();
}
let currentDate = new Date();
let events = {}; // { 'YYYY-MM-DD': [{ id, title }] }
let viewModal;

document.addEventListener("DOMContentLoaded", () => {
    // DOM elements
    const calendar = document.getElementById("calendar");
    const monthYear = document.getElementById("monthYear");
    const prevBtn = document.getElementById("prevMonth");
    const nextBtn = document.getElementById("nextMonth");
    const addEventBtn = document.getElementById("addEventBtn");
    const closeModalBtn = document.getElementById("closeModal");
    const closeViewModalBtn = document.getElementById("closeViewModal");
    const eventModalEl = document.getElementById("eventModal");
    viewModal = new bootstrap.Modal(document.getElementById("viewEventsModal"));
    //upcoming events
loadReminders();
    // --- Navigation ---
    prevBtn?.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    nextBtn?.addEventListener("click", () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // --- Modals ---
    addEventBtn?.addEventListener("click", () => {
        new bootstrap.Modal(eventModalEl).show();
    });

    closeModalBtn?.addEventListener("click", () => {
        bootstrap.Modal.getInstance(eventModalEl)?.hide();
    });

    closeViewModalBtn?.addEventListener("click", () => {
        document.getElementById("viewEventsModal").style.display = "none";
    });

    // Initial load
    fetchEvents();

    // --- Functions ---

    async function fetchEvents() {
        try {
            const res = await fetch("/get-events/");
            events = await res.json();
            renderCalendar();
        } catch (err) {
            console.error("Error fetching events:", err);
        }
    }

    async function saveEvent() {
        const date = document.getElementById("eventDate").value;
        const title = document.getElementById("eventTitle").value;

        if (!date || !title) return alert("Fill all fields");

        try {
            const res = await fetch("/add-event/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ date, title }),
            });
            const data = await res.json();
            if (data.status === "success") {
                await fetchEvents();
                document.getElementById("eventTitle").value = "";
                bootstrap.Modal.getInstance(eventModalEl)?.hide();
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error("Error saving event:", err);
        }
    }

    async function deleteEvent(date, index) {
        if (!confirm("Delete this task?")) return;

        const eventId = events[date][index].id;
        try {
            const res = await fetch("/delete-event/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ id: eventId }),
            });
            const data = await res.json();
            if (data.status === "success") await fetchEvents();
            else alert(data.message);
        } catch (err) {
            console.error("Error deleting event:", err);
        }
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    }

    function renderCalendar() {
        if (!calendar) return;

        calendar.innerHTML = "";

        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const firstDay = new Date(year, month, 1).getDay();
        const lastDate = new Date(year, month + 1, 0).getDate();

        monthYear.textContent = currentDate.toLocaleString("default", { month: "long", year: "numeric" });

        // Weekdays
        ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"].forEach(day => {
            const dayHeader = document.createElement("div");
            dayHeader.className = "weekday-header";
            dayHeader.textContent = day;
            calendar.appendChild(dayHeader);
        });

        // Empty slots
        for (let i = 0; i < firstDay; i++) calendar.innerHTML += "<div></div>";

        // Days
        for (let day = 1; day <= lastDate; day++) {
            const dateStr = `${year}-${String(month + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
            const dayDiv = document.createElement("div");
            dayDiv.className = "day";
            dayDiv.innerHTML = `<div class="day-number">${day}</div>`;

            if (events[dateStr]) {
                events[dateStr].slice(0, 2).forEach((event, index) => {
                    const eventEl = document.createElement("div");
                    eventEl.className = "event";

                    // Truncate title to 8 characters
                    const displayTitle = event.title.length > 8 ? event.title.slice(0, 8) + "…" : event.title;

                    eventEl.innerHTML = `
                        ${displayTitle}
                        <span style="cursor:pointer" onclick="deleteEvent('${dateStr}',${index})">✖</span>
                    `;
                    dayDiv.appendChild(eventEl);
                });

                if (events[dateStr].length > 2) {
                    const moreEl = document.createElement("div");
                    moreEl.className = "more-events";
                    moreEl.textContent = `+${events[dateStr].length - 2} more`;
                    moreEl.onclick = () => openViewModal(dateStr);
                    dayDiv.appendChild(moreEl);
                }
            }
            calendar.appendChild(dayDiv);
        }
    }

    function openViewModal(date) {
        const container = document.getElementById("allEventsContainer");
        const titleEl = document.getElementById("viewDateTitle");
        container.innerHTML = "";
        titleEl.textContent = date;

        events[date]?.forEach((event,index) => {
            const el = document.createElement("div");
            el.className = "event";
            el.innerHTML = `${event.title} <span onclick="deleteEvent('${date}',${index}); openViewModal('${date}')">✖</span>`;
            container.appendChild(el);
        });

        viewModal.show();
    }

    // Expose functions globally for inline onclicks
    window.saveEvent = saveEvent;
    window.deleteEvent = deleteEvent;
    window.openViewModal = openViewModal;
});

function loadReminders() {
    fetch("/upcoming-events/")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("reminderList");
            container.innerHTML = "";

            if (data.events.length === 0) {
                container.innerHTML = `<div class="empty">No upcoming events</div>`;
                return;
            }

            data.events.forEach(event => {
                const item = document.createElement("div");
                item.classList.add("reminder-item");

                item.innerHTML = `
                    <div class="reminder-icon">📅</div>
                    <div class="reminder-content">
                        <div class="title">${event.title}</div>
                        <div class="date">${event.date}</div>
                    </div>
                `;

                container.appendChild(item);
            });
        });
}

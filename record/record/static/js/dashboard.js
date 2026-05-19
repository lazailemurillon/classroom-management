‎document.addEventListener("DOMContentLoaded", () => {
‎    loadReminders();
‎
‎    fetch('/dashboard-stats/')
‎        .then(res => res.json())
‎        .then(data => {
‎            document.getElementById("totalClasses").textContent = data.classes;
‎            document.getElementById("totalStudents").textContent = data.students;
‎        });
‎
‎    //top students
‎    fetch('/dashboard/get-top-students/')
‎    .then(res => res.json())
‎    .then(data => {
‎
‎        const container = document.getElementById("topStudentsList");
‎
‎        // SAFETY CHECK (IMPORTANT)
‎        if (!Array.isArray(data)) {
‎            container.innerHTML = `
‎                <div class="text-muted small">
‎                    Loading top students...
‎                </div>
‎            `;
‎            return;
‎        }
‎
‎        if (data.length === 0) {
‎            container.innerHTML = `
‎                <div class="text-muted small">
‎                    No top students yet
‎                </div>
‎            `;
‎            return;
‎        }
‎
‎        container.innerHTML = data.map((s, index) => `
‎            <div class="top-student-card">
‎                <div>
‎                    <div class="fw-semibold">
‎                        ${index + 1}. ${s.name}
‎                    </div>
‎                    <div class="small text-muted">
‎                        Top Performer
‎                    </div>
‎                </div>
‎
‎                <div class="grade-badge">
‎                    ${s.average}%
‎                </div>
‎            </div>
‎        `).join("");
‎
‎    });
‎});
‎function loadReminders() {
‎    fetch("/upcoming-events/")
‎        .then(res => res.json())
‎        .then(data => {
‎            const container = document.getElementById("reminderList");
‎            container.innerHTML = "";
‎
‎            if (data.events.length === 0) {
‎                container.innerHTML = `<div class="empty">No upcoming events</div>`;
‎                return;
‎            }
‎
‎            data.events.forEach(event => {
‎                const item = document.createElement("div");
‎                item.classList.add("reminder-item");
‎
‎                item.innerHTML = `
‎                    <div class="reminder-icon">📅</div>
‎                    <div class="reminder-content">
‎                        <div class="title">${event.title}</div>
‎                        <div class="date">${event.date}</div>
‎                    </div>
‎                `;
‎
‎                container.appendChild(item);
‎            });
‎        });
‎
‎//attendance chart
‎fetch('/dashboard-attendance-analytics/')
‎        .then(res => res.json())
‎        .then(data => {
‎
‎            // =======================
‎            // LINE CHART (TREND)
‎            // =======================
‎
‎            const datasets = [];
‎
‎            Object.keys(data.trend).forEach((cls, index) => {
‎                datasets.push({
‎                    label: cls,
‎                    data: data.trend[cls].map(d => d.value),
‎                    fill: false,
‎                    tension: 0.3
‎                });
‎            });
‎
‎            const labels = Object.values(data.trend)[0]?.map(d => d.date) || [];
‎
‎            new Chart(document.getElementById("attendanceTrendChart"), {
‎                type: 'line',
‎                data: {
‎                    labels: labels,
‎                    datasets: datasets
‎                },
‎                options: {
‎                    responsive: true,
‎                    plugins: {
‎                        title: {
‎                            display: true,
‎                            text: 'Attendance Trend Over Time'
‎                        }
‎                    }
‎                }
‎            });
‎
‎            // =======================
‎            // BAR CHART (CLASS AVG)
‎            // =======================
‎
‎            new Chart(document.getElementById("attendanceBarChart"), {
‎                type: 'bar',
‎                data: {
‎                    labels: data.classes.map(c => c.name),
‎                    datasets: [{
‎                        label: 'Avg Attendance %',
‎                        data: data.classes.map(c => c.average)
‎                    }]
‎                },
‎                options: {
‎                    plugins: {
‎                        title: {
‎                            display: true,
‎                            text: 'Class Comparison'
‎                        }
‎                    }
‎                }
‎            });
‎
‎            // =======================
‎            // INSIGHTS
‎            // =======================
‎
‎            document.getElementById("worstDay").textContent = data.worst_day || "N/A";
‎
‎        });
‎
‎}

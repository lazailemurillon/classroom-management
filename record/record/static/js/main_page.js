document.addEventListener("DOMContentLoaded", function () {
    //------------------- tooltip -------------------
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    })

    // ------------------- LOGOUT -------------------
    const logoutBtn = document.getElementById("logoutBtn");
    logoutBtn.addEventListener("click", function (e) {
        e.preventDefault();
        if (confirm("Are you sure you want to logout?")) {
            window.location.href = "/logout/";
        }
    });
    
})

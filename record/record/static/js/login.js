document.querySelector("form").addEventListener("submit", function(e) {
    e.preventDefault();

    let formData = new FormData(this);

    fetch("", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    });
});

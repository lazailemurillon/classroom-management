document.addEventListener("DOMContentLoaded", function () {

    const form = document.querySelector("form");

    // Event listener for signup form submission
    form.addEventListener("submit", function(e) {
        e.preventDefault(); 

        const formData = new FormData(form);

        fetch("", {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);

            if (data.status === "success") {
                form.reset(); 
            }
        });
    });

});

window.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('plan-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        fetch('http://localhost:5000/generate_plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            // Do something with the response data here...
            console.log(data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});

window.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('plan-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const email = document.getElementById('email').value;  // Get email
        const heightFeet = document.getElementById('height-feet').value;
        const heightInches = document.getElementById('height-inches').value;
        const weight = document.getElementById('weight').value;
        const age = document.getElementById('age').value;
        const sex = document.getElementById('sex').value;
        const bmi = document.getElementById('bmi').value;
        const fitnessLevel = document.getElementById('fitness_level').value;
        const workoutType = document.getElementById('workout_type').value;  // Get workout type
        const goal = document.getElementById('goal').value;  // Get goal

        const data = {
            "email": email,  // Include email in data
            "height_feet": heightFeet,
            "height_inches": heightInches,
            "weight": weight,
            "age": age,
            "sex": sex,
            "bmi": bmi,
            "fitness_level": fitnessLevel,
            "workout_type": workoutType,
            "goal": goal
        };

        fetch('/generate_plan', {
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

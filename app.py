from flask import Flask, request, jsonify
import openai
import os
import boto3
from flask_cors import CORS
from threading import Thread

application = Flask(__name__)
CORS(application)  # Enable CORS on your Flask app



openai.api_key = os.getenv('OPENAI_API_KEY')



@application.route('/generate_plan', methods=['POST'])
def generate_plan():
    fitness_data = request.json

    if fitness_data is None:
        return jsonify({'message': 'No data provided'}), 400  # Bad Request
    required_keys = ["height", "weight", "age", "sex", "bmi", "fitness_level"]
    for key in required_keys:
        if key not in fitness_data:
            return jsonify({'message': f'Missing key in data: {key}'}), 400  # Bad Request
        
     # Start a new Thread to handle the request and immediately return a response to the user


    
    fitness_data = request.json
    workout_prompt = format_workout_prompt(fitness_data)
    meal_prompt = format_meal_prompt(fitness_data)

    workout_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=workout_prompt,
        temperature=0.5,
        max_tokens=2000
    )
    meal_response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=meal_prompt,
        temperature=0.5,
        max_tokens=2000
    )

    workout_plan = parse_workout_response(workout_response)
    meal_plan = parse_meal_response(meal_response)

    send_email(workout_plan, meal_plan)

    return jsonify({'message': 'Plans sent via email'})

def format_workout_prompt(fitness_data):
    # Determine the number of workout days based on fitness level
    fitness_level = fitness_data["fitness_level"]
    workout_type = fitness_data.get("workout_type", "general")  # Fetch workout type if present, otherwise default to "general"
    if fitness_level == "beginner":
        workout_days = 3
        exercise_rep_ranges = "3 sets of 8-10 reps"
    elif fitness_level == "intermediate":
        workout_days = 5
        exercise_rep_ranges = "3 sets of 10-12 reps"
    elif fitness_level == "advanced":
        workout_days = 6
        exercise_rep_ranges = "3 sets of 12-15 reps"
    else:
        workout_days = 3  # Default to 3 workout days for unknown fitness levels
        exercise_rep_ranges = "3 sets of 8-10 reps"  # Default rep range

    # Create a prompt for generating the workout plan
    prompt = (
        "As a NASM-certified personal trainer with 20 years of experience, I am helping a user create a workout plan. "
        "The user's details are as follows:\n"
        "Height: {}\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Workout Type: {}\n"
        "Based on this information, create a personalized {}-day workout plan with 5 exercises per day:\n\n"
    ).format(
        fitness_data["height"],
        fitness_data["weight"],
        fitness_data["age"],
        fitness_data["sex"],
        fitness_data["bmi"],
        fitness_data["fitness_level"],
        workout_type,
        workout_days,
    )

    # Add exercise prompts for each day
    for day in range(1, workout_days + 1):
        prompt += f"Day {day}:\n"
        for exercise_num in range(1, 6):
            prompt += f"Exercise {exercise_num}: [Exercise Name] - {exercise_rep_ranges}\n"
        prompt += "\n"

    return prompt


def format_meal_prompt(fitness_data):
    # Create a prompt for generating the meal plan
    prompt = (
        "As a nutritionist with 20 years of experience, I am helping a user create a personalized 7-day meal plan. "
        "The user's details are as follows:\n"
        "Height: {}\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Based on this information, create a personalized 7-day meal plan that includes breakfast, snack 1, lunch, snack 2, and dinner with ingredients, calorie count per ounce for each ingredient, serving sizes, and total calories for the meal:"
    ).format(
        fitness_data["height"], 
        fitness_data["weight"], 
        fitness_data["age"], 
        fitness_data["sex"], 
        fitness_data["bmi"], 
        fitness_data["fitness_level"]
    )

    meals = ['Breakfast', 'Snack 1', 'Lunch', 'Snack 2', 'Dinner']

    # Repeat this pattern for all 7 days
    for day in range(1, 8):
        prompt += f"\n\nDay {day}:\n"
        for meal in meals:
            prompt += (
                f"{meal}: [Meal Name] - Ingredients: [Ingredients with calorie count per oz], "
                "Serving Size: [Serving Size], Total Calories: [Total Calories]\n"
            )

    return prompt




def parse_workout_response(response):
    # Extract the relevant information from the GPT-3 response.
    # Format the workout plan as a 1-week plan with 5-6 exercises per day.
    plan_text = response.choices[0].text.strip()
    plan_lines = plan_text.split("\n")

    formatted_plan = ""
    for i, line in enumerate(plan_lines):
        if i % 8 == 0:
            formatted_plan += "\n"  # Add line break every 8 lines (1-day plan)
        formatted_plan += line.strip() + "\n"

    return formatted_plan


def parse_meal_response(response):
    # Extract the relevant information from the GPT-3 response.
    # Format the meal plan as a 1-week plan with breakfast, lunch, dinner, and snacks.
    plan_text = response.choices[0].text.strip()
    plan_lines = plan_text.split("\n")

    formatted_plan = ""
    for i, line in enumerate(plan_lines):
        if i % 8 == 0:
            formatted_plan += "\n"  # Add line break every 8 lines (1-day plan)
        formatted_plan += line.strip() + "\n"

    return formatted_plan


def send_email(workout_plan, meal_plan):
    # Set up the email
    sender_email = "youremail.com"
    receiver_email = "youremail.com"
    subject = "Personalized Workout and Meal Plans"
    message = f"""
    Hello,

    Here are your personalized workout and meal plans:

    Workout Plan:
    {workout_plan}

    Meal Plan:
    {meal_plan}

    Enjoy your fitness journey!

    Regards,
    Your Personal Trainer
    """

    # Create an SES client
    ses_client = boto3.client('ses', region_name='us-east-1')

    # Send the email
    response = ses_client.send_email(
        Source=sender_email,
        Destination={
            'ToAddresses': [receiver_email]
        },
        Message={
            'Subject': {
                'Data': subject
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        }
    )


if __name__ == '__main__':
    application.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

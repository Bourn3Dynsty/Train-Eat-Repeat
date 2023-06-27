from flask import Flask, request, jsonify,render_template
import openai
import os
import boto3
from flask_cors import CORS
from threading import Thread
import random
import PyPDF2
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS on your Flask app

openai.api_key = os.getenv('OPENAI_API_KEY')
file_path = r"C:\Users\mdibiaso\Repos\Train-Eat-Repeat\6daysplit.pdf"

# Set up the logger
logging.basicConfig(level=logging.DEBUG)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    fitness_data = request.json

    
    
    keys = list(fitness_data.keys())
    logging.debug(fitness_data)  # Use logging instead of print
  

    if fitness_data is None:
        print(fitness_data)
        return jsonify({'message': 'No data provided'}), 400  # Bad Request

    required_keys = ["height_feet", "height_inches", "weight", "age", "sex", "bmi", "fitness_level", "goal", "email"]

    print(list(fitness_data.keys()))  # Print the keys in the received data
    for key in required_keys:
        if key not in fitness_data:
            return jsonify({'message': f'Missing key in data: {key}'}), 400

    goal = fitness_data["goal"]
    if goal == "fat_loss":
        workout_prompt = format_fat_loss_workout_prompt(fitness_data)  # Update this line
    elif goal == "bodybuilding":
        workout_prompt = format_bodybuilding_workout_prompt(fitness_data)
    else:
        workout_prompt = format_workout_prompt(fitness_data)  # Update this line for the general workout plan

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

    receiver_email = fitness_data.get('email')  # Get the email from the form data
    send_email(receiver_email, workout_plan, meal_plan)  # Pass the email to the send_email function

    return jsonify({'message': 'Cooking something good!. The plans will be sent via email'})

def read_pdf(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    num_pages = pdf_reader.numPages

    content = ""
    for i in range(num_pages):
        page_obj = pdf_reader.getPage(i)
        content += page_obj.extractText()

    pdf_file_obj.close()
    return content



def format_workout_prompt(fitness_data):
    # Determine the number of workout days based on fitness level
    fitness_level = fitness_data["fitness_level"]
    workout_type = fitness_data.get("workout_type", "general")  # Fetch workout type if present, otherwise default to "general"

    if fitness_level == "beginner":
        workout_days = 3
    elif fitness_level == "intermediate":
        workout_days = 5
    elif fitness_level == "advanced":
        workout_days = 6
    else:
        workout_days = 3  # Default to 3 workout days for unknown fitness levels

    # Create a prompt for generating the workout plan
    prompt = (
        "Based on this information, create a personalized {}-day workout plan with 5 exercises per day:\n\n"
        "Height (feet): {}\n"
        "Height (inches): {}\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Workout Type: {}\n"
).format(
    workout_days,
    fitness_data["height_feet"],
    fitness_data["height_inches"],
    fitness_data["weight"],
    fitness_data["age"],
    fitness_data["sex"],
    fitness_data["bmi"],
    fitness_data["fitness_level"],
    workout_type
)

    # Add exercise prompts for each day
    for day in range(1, workout_days + 1):
        if workout_type == "fat_loss":
            prompt += f"Day {day} (Steady-State Cardio and Light Weights):\n"
        elif workout_type == "body_building":
            if day % 3 == 1:
                prompt += f"Day {day} (Push):\n"
            elif day % 3 == 2:
                prompt += f"Day {day} (Pull):\n"
            else:
                prompt += f"Day {day} (Legs):\n"
        else:  # For general or unknown workout type
            prompt += f"Day {day}:\n"

        for exercise_num in range(1, 8):
            if fitness_level == "beginner":
                exercise_rep_ranges = "3 sets of 8-10 reps"
            elif fitness_level == "intermediate":
                exercise_rep_ranges = "3 sets of 10-12 reps"
            elif fitness_level == "advanced":
                exercise_rep_ranges = "4 sets of 12-15 reps"
            else:
                exercise_rep_ranges = "3 sets of 8-10 reps"  # Default rep range

            prompt += f"Exercise {exercise_num}: [Exercise Name] - {exercise_rep_ranges}\n"
        prompt += "\n"

    return prompt



def format_fat_loss_workout_prompt(fitness_data):
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

    # Retrieve the height value from the form field
    height = fitness_data["height"]

    # Create a prompt for generating the workout plan
    prompt = (
        "As a NASM-certified personal trainer with 20 years of experience, I am helping a user create a workout plan for fat loss that has steady state cardio and a little bit of light weights"
        "The user's details are as follows:\n"
        "Height: {}\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Workout Type: {}\n"
        "Based on this information and the goal of fat loss, create a personalized {}-day workout plan with 5-8 exercises per day steady state cardio and light weight excercises depending on fitness level:\n\n"
    ).format(
        height,
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
            prompt += f"Exercise {exercise_num}: [Cardio Exercise Name] - {exercise_rep_ranges}\n"
        prompt += "\n"

    return prompt



def format_bodybuilding_workout_prompt(fitness_data, file_path):
    pdf_content = read_pdf(file_path)
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
        "As a IFBB Pro BodyBuilder with 20 years of experience, I am helping a user create a bodybuilding workout plan. "
        "The user's details are as follows:\n"
        "Height: {}\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Workout Type: {}\n"
        "Workout Plans from PDF: {}\n"
        "Based on this information and the goal of bodybuilding, create a personalized {}-day push-pull-legs (PPL) workout plan with 5-9 exercises per day depending on fitness level that focuses on making upper body push and pull and 1-2 dedicated legs splits do not repeat expercises:\n\n"
    ).format(
        fitness_data["height"],
        fitness_data["weight"],
        fitness_data["age"],
        fitness_data["sex"],
        fitness_data["bmi"],
        fitness_data["fitness_level"],
        workout_type,
        workout_days,
        pdf_content
    )

    # Add exercise prompts for each day
    for day in range(1, workout_days + 1):
        prompt += f"Day {day}:\n"
        prompt += "Push:\n"
        for exercise_num in range(1, 6):
            prompt += f"Exercise {exercise_num}: [Push Exercise Name] - {exercise_rep_ranges}\n"
        prompt += "\n"

        prompt += "Pull:\n"
        for exercise_num in range(1, 6):
            prompt += f"Exercise {exercise_num}: [Pull Exercise Name] - {exercise_rep_ranges}\n"
        prompt += "\n"

        prompt += "Legs:\n"
        for exercise_num in range(1, 6):
            prompt += f"Exercise {exercise_num}: [Legs Exercise Name] - {exercise_rep_ranges}\n"
        prompt += "\n"

    return prompt




def format_meal_prompt(fitness_data):
    # Create a prompt for generating the meal plan
    prompt = (
        "As a nutritionist with 20 years of experience, I am helping a user create a personalized 7-day meal plan. "
        "The user's details are as follows:\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Based on this information, create a personalized 7-day meal plan that includes breakfast, snack 1, lunch, snack 2, and dinner with ingredients, calorie count per ounce for each ingredient, serving sizes, and total calories for the meal:"
    ).format(
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


def send_email(receiver_email, workout_plan, meal_plan):
    # Set up the email
    sender_email = os.getenv("SENDER_EMAIL")
    subject = "Personalized Workout and Meal Plans"

    # Generate a random motivational quote
    motivational_quotes = [
        "Believe in yourself, there's something inside you that is greater than any obstacle.",
        "Success starts with self-discipline.",
        "You are one workout away from a good mood.",
        "Your body can stand almost anything. It’s your mind you have to convince.",
        "Sweat is just fat crying.",
        "The only bad workout is the one that didn't happen.",
        "Challenges are what make life interesting. Overcoming them is what makes them meaningful.",
    ]
    random_quote = random.choice(motivational_quotes)

    # Add content to the message
    message_body = f"""
    Hello,

    Here are your personalized workout and meal plans:

    Workout Plan:
    {workout_plan}

    Meal Plan:
    {meal_plan}

    Remember, consistency is key. Stick to your plan and enjoy your fitness journey.

    Quote of the Day:
    "{random_quote}" 💪

    Let's make fitness a lifestyle!

    Best,
    [Your Name]
    """

    # Create an AWS SES client
    client = boto3.client("ses", region_name="us-east-1")  # Replace 'us-east-1' with your desired region

    # Send the email
    response = client.send_email(
        Source=sender_email,
        Destination={"ToAddresses": [receiver_email]},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Text": {"Data": message_body}},
        },
    )

    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
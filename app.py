from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')

@application.route('/generate_plan', methods=['POST'])
def generate_plan():
    fitness_data = request.json
    prompt = format_prompt(fitness_data)

    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      temperature=0.5,
      max_tokens=200
    )

    plan = parse_gpt_response(response)
    return jsonify(plan)

def format_prompt(fitness_data):
    # Here you need to create a string that instructs GPT-3 on what text to generate. 
    # This will depend on the structure of your fitness_data and the kind of plan you want to generate.
    prompt = (
        "As a NASM-certified personal trainer with 20 years of experience, I am helping a user create a workout plan. "
        "The user's details are as follows:\n"
        "Height: {}\n"
        "Weight: {}\n"
        "Age: {}\n"
        "Sex: {}\n"
        "BMI: {}\n"
        "Fitness Level: {}\n"
        "Based on this information, create a personalized 5 day workout plan:"
    ).format(
        fitness_data["height"], 
        fitness_data["weight"], 
        fitness_data["age"], 
        fitness_data["sex"], 
        fitness_data["bmi"], 
        fitness_data["fitness_level"]
    )
    return prompt

def parse_gpt_response(response):
    # Extract the relevant information from the GPT-3 response. 
    # Here, we just return the generated text, but you might need to process it further depending on your needs.
    return {'plan': response.choices[0].text.strip()}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))


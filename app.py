from flask import Flask, request, jsonify
import requests
from langchain_anthropic import ChatAnthropic
from crewai import Crew, Process, Agent, Task
from dotenv import load_dotenv
import os
from langsmith import traceable

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = 'appPcWNUeei7MNMCj'
AIRTABLE_TABLE_NAME = 'tblaMtAcnVa4nwnby'
AIRTABLE_FIELD_ID = 'fldgHGVaxSj1irPpF'

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Use the ChatAnthropic instance directly
client = ChatAnthropic(model="claude-3-sonnet-20240229", max_tokens=4069, api_key=ANTHROPIC_API_KEY)

Nutritionist = Agent(
    role='Nutritionist',
    goal=f'prescribe healthy meal plan',
    backstory=f""" you are an expert nutritonist""",
    verbose=False,
    allow_delegation=True,
    max_rpm=5,
    llm=client
)

diet_task = Task(
    description=f"""a balanced diet meal plan """,
    expected_output=f"""  300 words maximum, a healthy meal plan""",
    output_file='diet_report4.docx',
)

# Define a route for the root URL
@app.route('/')
def root():
    return "Welcome to the Flask application!"

@app.route('/run_task', methods=['GET'])
@traceable  # Auto-trace this function
def run_task():
    project_crew = Crew(
        tasks=[diet_task],
        agents=[Nutritionist],
        manager_llm=client,
        max_rpm=4,
        process=Process.hierarchical
    )

    result = project_crew.kickoff()

    # Send the output data to Airtable
    send_to_airtable({'result': result})

    return jsonify({'message': 'Task completed successfully'})

def send_to_airtable(data):
    url = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'
    headers = {
        'Authorization': f'Bearer {AIRTABLE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'records': [
            {
                'fields': {
                    AIRTABLE_FIELD_ID: data['result']
                }
            }
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

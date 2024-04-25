from flask import Flask, request, jsonify
import requests
from langchain_anthropic import ChatAnthropic
from crewai import Crew, Process, Agent, Task
from dotenv import load_dotenv
import os
import logging
from langsmith import Langsmith

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Configure Langsmith
LANGSMITH_API_KEY = os.getenv('LANGSMITH_API_KEY')
langsmith = Langsmith(LANGSMITH_API_KEY)
logger = langsmith.get_logger(__name__)

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = 'appPcWNUeei7MNMCj'
AIRTABLE_TABLE_NAME = 'tblaMtAcnVa4nwnby'
AIRTABLE_FIELD_ID = 'fldgHGVaxSj1irPpF'

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

Nutritionist = Agent(
    role='Nutritionist',
    goal=f'prescribe healthy meal plan',
    backstory=f""" you are an expert nutritonist""",
    verbose=False,
    allow_delegation=True,
    max_rpm=5,
    llm=ChatAnthropic(model="claude-3-sonnet-20240229", max_tokens=4069, api_key=ANTHROPIC_API_KEY)
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
def run_task():
    logger.info("Received request to run CrewAI task")

    project_crew = Crew(
        tasks=[diet_task],
        agents=[Nutritionist],
        manager_llm=ChatAnthropic(temperature=1, model="claude-3-sonnet-20240229", max_tokens=4069),
        max_rpm=4,
        process=Process.hierarchical
    )

    logger.info("Starting CrewAI task execution")
    result = project_crew.kickoff()
    logger.info("CrewAI task execution completed")

    logger.info(f"Result: {result}")

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
    app.run()

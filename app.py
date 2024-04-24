from flask import Flask, request, jsonify
import requests
from langchain_anthropic import ChatAnthropic
from crewai import Crew, Process, Agent, Task
from dotenv import load_dotenv
import os
import logging

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ... (Airtable configuration and other code) ...

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

# ... (send_to_airtable function and other code) ...

if __name__ == '__main__':
    app.run()

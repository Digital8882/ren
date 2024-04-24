from flask import Flask, request, jsonify
import requests
from langchain_anthropic import ChatAnthropic
from crewai import Crew, Process, Agent, Task
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)

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

# Rest of your code remains the same
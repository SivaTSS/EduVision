import os
import json
from langchain_openai import ChatOpenAI

# Load API keys from the JSON file.
file_path = "../keys.json"
with open(file_path, "r", encoding="utf-8") as file:
    key_data = json.load(file)

# Set the OpenAI API key environment variable.
os.environ["OPENAI_API_KEY"] = key_data["openai_api_key"]

# Set up the LLM.
model_name = "gpt-4o-mini"
llm = ChatOpenAI(temperature=0, model_name=model_name)

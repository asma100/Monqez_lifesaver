import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

model = genai.GenerativeModel("models/gemini-2.5-pro")
response = model.generate_content("What is CPR?")
print(response.text)

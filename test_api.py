import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads the .env file

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Say hello in one short sentence.",
)

print(response.text)
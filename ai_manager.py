import io_manager
import os
from dotenv import load_dotenv
from google import genai

# Reads the .env file (which contains the API key)
load_dotenv()

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain how AI works in a few words"
)
print(interaction.output_text)
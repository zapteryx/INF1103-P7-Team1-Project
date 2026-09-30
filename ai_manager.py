import io_manager
from dotenv import load_dotenv
from google import genai

# Maintained by Mei Qi (2605039)
# Reads the .env file (which contains the API key)
load_dotenv()

# Load the shelter data using functions from io_manager
file_path = io_manager.get_shelter_filename()
shelters = io_manager.load_shelters_from_csv(file_path)

# Convert each shelter dict to text and join them
shelter_info = "\n".join(io_manager.format_shelter(s) for s in shelters)

# Retrieve the client info using functions from io_manager
client_info = io_manager.collect_intake_input()

# Create a prompt using the shelter and client info
prompt = f"""Based on the client and shelter information shown, determine the urgency level of the case 
    (from 1-5, where 5 is the most urgent and 1 is the least urgent), give a structured JSON dictionary of criterias 
    that the shelter meets for the case, and provide a recommended shelter for the candidate.\n 
    Client info:\n {client_info} \nShelter info:\n {shelter_info}"""

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-3.8-flash",
    input=prompt
)
print(interaction.output_text)
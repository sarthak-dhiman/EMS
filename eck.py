from dotenv import load_dotenv
import os

# Try to load the .env file
load_dotenv()

# Read the variable
url = os.getenv("DATABASE_URL")

print("--------------------------------------------------")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Value of DATABASE_URL: {url}")
print("--------------------------------------------------")

if not url:
    print("❌ ERROR: .env file not loaded or empty.")
else:
    print("✅ SUCCESS: .env file found.")
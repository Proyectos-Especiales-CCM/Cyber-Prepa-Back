import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the testing environment variable
is_testing = os.getenv("TESTING", "false").lower() == "true"

# Initialize Supabase client only if not in testing mode
if not is_testing:
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    
    if url and key:
        supabase: Client = create_client(url, key)
    else:
        raise ValueError("Supabase URL and Key must be provided.")
else:
    supabase = None  # Set supabase to None or a mock object during testing
    print("Running in testing mode. Supabase client not initialized.")

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from unittest.mock import Mock

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
    # Define a mock for the supabase client
    supabase = Mock()

    # Mock the methods you need for your tests
    supabase.storage.from_.return_value.get_public_url.return_value = "mocked_public_url"
    supabase.storage.from_.return_value.upload.return_value = Mock(status_code=200)
    supabase.storage.from_.return_value.remove.return_value = {"status_code": 200}

    print("Running in testing mode. Supabase client mocked.")

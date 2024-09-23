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
    supabase.storage.from_.return_value.get_public_url.return_value = (
        "mocked_public_url"
    )
    supabase.storage.from_.return_value.upload.return_value = Mock(status_code=200)
    supabase.storage.from_.return_value.remove.return_value = [
        {
            "name": "images/image.webp",
            "bucket_id": "Cyberprepa",
            "owner": "",
            "owner_id": "",
            "version": "2afc4435-66ef-4542-9336-f6b92ec90224",
            "id": "a96ac2fc-6a31-4d08-baef-240103b068ee",
            "updated_at": "2024-09-23T03:58:50.128Z",
            "created_at": "2024-09-23T03:58:50.128Z",
            "last_accessed_at": "2024-09-23T03:58:50.128Z",
            "metadata": {
                "eTag": '"e10b92c1bbb2448ff6387e4746cf94bc"',
                "size": 5530,
                "mimetype": "image/webp",
                "cacheControl": "no-cache",
                "lastModified": "2024-09-23T03:58:51.000Z",
                "contentLength": 5530,
                "httpStatusCode": 200,
            },
            "user_metadata": {},
        }
    ]

    print("Running in testing mode. Supabase client mocked.")

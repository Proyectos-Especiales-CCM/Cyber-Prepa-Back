from dataclasses import dataclass

from django.conf import settings
from google.cloud import storage


@dataclass
class OperationResponse:
    message: str
    status_code: int


class GCSStorageClient:
    """Wrapper for Google Cloud Storage operations to match the expected API."""

    def __init__(self, bucket_name: str, folder: str = ""):
        # Use Application Default Credentials
        self.client = storage.Client()
        self.bucket_name = bucket_name
        self.bucket = self.client.bucket(bucket_name)
        self.folder = f"{folder.strip('/')}/" if folder else ""

    def upload(self, file, path: str, file_options: dict = None):
        """Upload a file to GCS.

        Args:
            file: File-like object to upload
            path: Destination path in the bucket
            file_options: Dict with 'content-type' key

        Returns:
            Mock object with status_code=200 on success
        """
        full_path = f"{self.folder}{path}"
        blob = self.bucket.blob(full_path)
        content_type = (
            file_options.get("content-type") if file_options else None
        )

        # Reset file pointer to beginning
        file.seek(0)
        blob.upload_from_file(file, content_type=content_type)

        # Return a mock response with status_code for compatibility
        response = OperationResponse(
            message="File uploaded successfully", status_code=200
        )
        return response

    def get_public_url(self, path: str) -> str:
        """Get the public URL for a blob.

        Args:
            path: Path to the blob in the bucket

        Returns:
            Public URL string
        """
        blob = self.bucket.blob(path)
        print(blob.public_url)
        return blob.public_url

    def remove(self, path: str) -> OperationResponse:
        """Remove one or more blobs from GCS.

        Args:
            path: Path to the blob to remove

        Returns:
            OperationResponse with status_code=200 on success
        """
        blob = self.bucket.blob(path)
        blob.delete()
        return OperationResponse(
            message="File deleted successfully", status_code=200
        )


class MockStorageClient:
    """Mock storage client for testing."""

    def __init__(self, bucket_name: str, folder: str = ""):
        self.bucket_name = bucket_name
        self.folder = f"{folder.strip('/')}/" if folder else ""

    def upload(self, *args, **kwargs):
        response = OperationResponse(
            message="File uploaded successfully", status_code=200
        )
        return response

    def get_public_url(self, *args, **kwargs) -> str:
        return "https://avatars.githubusercontent.com/u/85468901?s=96&v=4"

    def remove(self, *args, **kwargs) -> OperationResponse:
        return OperationResponse(
            message="File deleted successfully", status_code=200
        )


# Initialize storage client
if not settings.DEBUG:
    storage_client = GCSStorageClient(
        getattr(settings, "BUCKET_NAME", "bucket-name")
    )
else:
    # Use mock client for development/testing
    storage_client = MockStorageClient(
        getattr(settings, "BUCKET_NAME", "bucket-name")
    )

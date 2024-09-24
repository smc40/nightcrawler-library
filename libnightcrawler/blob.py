import json
import logging
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential


class BlobClient:
    def __init__(self, settings):
        self.settings = settings
        self._service_client: BlobServiceClient | None = None

    @property
    def service_client(self) -> BlobServiceClient:
        """Lazy initialization of Azure blob storage client"""
        if self._service_client is None:
            self._service_client = (
                BlobServiceClient.from_connection_string(self.settings.connection_string)
                if not self.settings.account_url
                else BlobServiceClient(
                    self.settings.account_url, credential=DefaultAzureCredential()
                )
            )
        return self._service_client

    def _put_object(self, container: str, path: str, image: bytes | str):
        logging.info("Puting object to container: %s", container)
        client = self.service_client.get_blob_client(container=container, blob=path)
        return client.upload_blob(image, overwrite=True)

    def _get_object(self, container: str, path: str) -> bytes:
        logging.info("Getting object from container: %s path %s", container, path)
        client = self.service_client.get_blob_client(container=container, blob=path)
        data = client.download_blob().readall()
        return data

    def put_processing(self, path: str, data: dict):
        logging.warning("Puting process file: %s", path)
        self._put_object(self.settings.process_container, path, json.dumps(data))

    def put_image(self, path: str, image: bytes):
        logging.warning("Puting image: %s", path)
        self._put_object(self.settings.image_container, path, image)

    def get_image(self, path: str) -> bytes:
        logging.warning("Puting image: %s", path)
        return self._get_object(self.settings.image_container, path)

    def make_public(self, path: str):
        logging.warning("Copying to public container: %s", path)
        data = self.get_image(path)
        self._put_object(self.settings.public_container, path, data)
        return "/".join([self.settings.account_url, self.settings.public_container, path])

    def remove_from_public(self, path: str):
        logging.warning("Removing from public container: %s", path)
        client = self.service_client.get_blob_client(
            container=self.settings.public_container, blob=path
        )
        client.delete_blob()

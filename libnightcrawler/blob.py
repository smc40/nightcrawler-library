import json
import logging
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential
import azure.core.exceptions


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

    def _put_object(self, container: str, path: str, image: bytes | str, cs: ContentSettings | None = None):
        logging.info("Puting object to container: %s", container)
        client = self.service_client.get_blob_client(container=container, blob=path)
        if cs is None:
            cs = ContentSettings()
        return client.upload_blob(image, overwrite=True, content_settings=cs)

    def _get_object(self, container: str, path: str) -> bytes:
        logging.info("Getting object from container: %s path %s", container, path)
        client = self.service_client.get_blob_client(container=container, blob=path)
        data = client.download_blob().readall()
        return data

    def put_processing(self, path: str, data: dict):
        logging.warning("Puting process file: %s", path)
        self._put_object(self.settings.process_container, path, json.dumps(data))

    def put_image(self, path: str, image: bytes, content_type: str | None):
        logging.warning("Puting image: %s", path)
        settings = ContentSettings(content_type=content_type)
        self._put_object(self.settings.image_container, path, image, settings)

    def get_image(self, path: str) -> bytes:
        logging.warning("Puting image: %s", path)
        return self._get_object(self.settings.image_container, path)

    def image_exists(self, path: str) -> bool:
        blob = self.service_client.get_blob_client(container=self.settings.image_container, blob=path)
        return blob.exists()

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

    def cache(self, path, content):
        logging.info("Caching file %s", path)
        self._put_object(self.settings.process_container, path, json.dumps(content))

    def get_cached(self, path: str, expiry: int) -> bytes | None:
        blob = self.service_client.get_blob_client(container=self.settings.process_container, blob=path)
        try:
            properties = blob.get_blob_properties()
        except azure.core.exceptions.ResourceNotFoundError:
            return None
        date = properties.last_modified
        if (datetime.now(timezone.utc) - date).total_seconds() >= expiry:
            logging.info("%s exists but is obsolete for TTL (%d)", path, expiry)
            return None
        return json.loads(blob.download_blob().readall())

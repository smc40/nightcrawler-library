from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class SendgridSettings(BaseSettings):
    api_key: str = ""
    from_address: str = ""
    frontend_dns_url: str = ""
    email_is_sandbox_mode: bool = False
    model_config = SettingsConfigDict(env_prefix="nightcrawler_sendgrid_")


class PostgresSettings(BaseSettings):
    user: str = "user"
    password: str = "secret"
    host: str = "127.0.0.1"
    port: int = 5432
    name: str = "nightcrawler"
    auto_migrate: bool = True
    migration_failure_allowed: bool = False
    model_config = SettingsConfigDict(env_prefix="nightcrawler_postgres_")

    @property
    def connection_string(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?sslmode=prefer"


class BlobSettings(BaseSettings):
    image_container: str = "images"
    process_container: str = "processing"
    public_container: str = "public"
    connection_string: str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    account_url: str = ""
    model_config = SettingsConfigDict(env_prefix="nightcrawler_blob_")


class Settings(BaseSettings):
    postgres: PostgresSettings = Field(default_factory=PostgresSettings)
    sendgrid: SendgridSettings = Field(default_factory=SendgridSettings)
    blob: BlobSettings = Field(default_factory=BlobSettings)
    use_file_storage: bool = True
    organizations_path: str = "tests/organizations.json"
    model_config = SettingsConfigDict(env_prefix="nightcrawler_")

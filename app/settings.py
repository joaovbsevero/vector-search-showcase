from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class QDrantConfig(BaseSettings):
    collection_name: str

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=False,
        env_prefix="VECTOR_SEARCH_APP_QDRANT_",
    )

    @staticmethod
    @lru_cache()
    def get_settings() -> "QDrantConfig":
        return QDrantConfig()  # type: ignore


class MilvusConfig(BaseSettings):
    collection_name: str

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=False,
        env_prefix="VECTOR_SEARCH_APP_MILVUS_",
    )

    @staticmethod
    @lru_cache()
    def get_settings() -> "MilvusConfig":
        return MilvusConfig()  # type: ignore


class MongoDBConfig(BaseSettings):
    uri: str
    db_name: str
    collection_name: str

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=False,
        env_prefix="VECTOR_SEARCH_APP_MONGODB_",
    )

    @staticmethod
    @lru_cache()
    def get_settings() -> "MongoDBConfig":
        return MongoDBConfig()  # type: ignore


class PineconeConfig(BaseSettings):
    api_key: str
    index_name: str

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=False,
        env_prefix="VECTOR_SEARCH_APP_PINECONE_",
    )

    @staticmethod
    @lru_cache()
    def get_settings() -> "PineconeConfig":
        return PineconeConfig()  # type: ignore


class Settings(BaseSettings):
    # Streamlit config
    streamlit_server_port: int
    streamlit_server_address: str

    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env",
        case_sensitive=False,
        env_prefix="VECTOR_SEARCH_APP_",
    )

    @property
    def qdrant_database_config(self) -> QDrantConfig:
        if hasattr(self, "_qdrant_database_config"):
            return getattr(self, "_qdrant_database_config")

        setattr(self, "_qdrant_database_config", QDrantConfig.get_settings())
        return getattr(self, "_qdrant_database_config")

    @property
    def milvus_database_config(self) -> MilvusConfig:
        if hasattr(self, "_milvus_database_config"):
            return getattr(self, "_milvus_database_config")

        setattr(self, "_milvus_database_config", MilvusConfig.get_settings())
        return getattr(self, "_milvus_database_config")

    @property
    def mongodb_database_config(self) -> MongoDBConfig:
        if hasattr(self, "_mongodb_database_config"):
            return getattr(self, "_mongodb_database_config")

        setattr(self, "_mongodb_database_config", MongoDBConfig.get_settings())
        return getattr(self, "_mongodb_database_config")

    @property
    def pinecone_database_config(self) -> PineconeConfig:
        if hasattr(self, "_pinecone_database_config"):
            return getattr(self, "_pinecone_database_config")

        setattr(self, "_pinecone_database_config", PineconeConfig.get_settings())
        return getattr(self, "_pinecone_database_config")

    @staticmethod
    @lru_cache()
    def get_settings() -> "Settings":
        return Settings()  # type: ignore

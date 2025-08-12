import pytest
from pydantic import ValidationError

from mongodb_rooms_pkg.configuration.addonconfig import CustomAddonConfig
from mongodb_rooms_pkg.configuration.baseconfig import BaseAddonConfig


class TestBaseAddonConfig:
    def test_base_config_creation(self):
        config = BaseAddonConfig(
            id="test_addon_id",
            type="test_type",
            name="test_addon",
            description="Test addon description",
            secrets={"key1": "value1"}
        )

        assert config.id == "test_addon_id"
        assert config.type == "test_type"
        assert config.name == "test_addon"
        assert config.description == "Test addon description"
        assert config.secrets == {"key1": "value1"}
        assert config.enabled is True

    def test_base_config_defaults(self):
        config = BaseAddonConfig(
            id="test_id",
            type="test_type",
            name="test",
            description="Test description"
        )

        assert config.enabled is True
        assert config.secrets == {}
        assert config.config == {}


class TestCustomAddonConfig:
    def test_custom_config_creation_success(self):
        config = CustomAddonConfig(
            id="test_mongodb_addon_id",
            name="test_mongodb_addon",
            description="Test MongoDB addon",
            type="storage",
            host="localhost",
            database="testdb",
            secrets={"db_password": "secret", "db_user": "user"}
        )

        assert config.id == "test_mongodb_addon_id"
        assert config.name == "test_mongodb_addon"
        assert config.type == "storage"
        assert config.host == "localhost"
        assert config.database == "testdb"
        assert config.port == 27017

    def test_custom_config_with_custom_values(self):
        config = CustomAddonConfig(
            id="test_mongodb_addon_id",
            name="test_mongodb_addon",
            description="Test MongoDB addon",
            type="storage",
            host="localhost",
            database="testdb",
            port=27018,
            scheme="mongodb+srv",
            secrets={"db_password": "secret", "db_user": "user"}
        )

        assert config.port == 27018
        assert config.scheme == "mongodb+srv"

    def test_custom_config_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CustomAddonConfig(
                id="test_mongodb_addon_id",
                name="test_mongodb_addon",
                description="Test MongoDB addon",
                secrets={"db_password": "secret", "db_user": "user"}
            )

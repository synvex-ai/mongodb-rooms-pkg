from unittest.mock import MagicMock, patch

import pytest

from mongodb_rooms_pkg.addon import MongoDBRoomsAddon
from mongodb_rooms_pkg.configuration.addonconfig import CustomAddonConfig


def get_base_config():
    return {
        "id": "test",
        "type": "mongodb",
        "name": "Test Config",
        "description": "Test configuration"
    }


class TestMongoDBRoomsAddon:
    def test_addon_initialization(self):
        addon = MongoDBRoomsAddon()
        assert addon.type == "storage"
        assert addon.config is None
        assert addon.connection is None
        assert addon.modules == ["actions", "configuration", "memory", "services", "storage", "tools", "utils"]

    def test_load_addon_config_valid(self):
        addon = MongoDBRoomsAddon()
        test_config = {
            **get_base_config(),
            "host": "localhost",
            "database": "testdb",
            "secrets": {"db_user": "user", "db_password": "pass"}
        }

        with patch.object(addon, 'initConnection', return_value=True):
            result = addon.loadAddonConfig(test_config)
            assert result is True
            assert isinstance(addon.config, CustomAddonConfig)
            assert addon.config.host == "localhost"
            assert addon.config.database == "testdb"

    def test_load_addon_config_missing_required(self):
        addon = MongoDBRoomsAddon()
        test_config = {
            "id": "test",
            "type": "mongodb",
            "name": "Test Config",
            "description": "Test configuration"
        }

        result = addon.loadAddonConfig(test_config)
        assert result is False

    @patch('mongodb_rooms_pkg.addon.create_connection')
    def test_init_connection_success(self, mock_create_connection):
        mock_connection = MagicMock()
        mock_create_connection.return_value = mock_connection

        addon = MongoDBRoomsAddon()
        addon.config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )

        result = addon.initConnection()
        assert result is True
        assert addon.connection == mock_connection

    @patch('mongodb_rooms_pkg.addon.create_connection')
    def test_init_connection_failure(self, mock_create_connection):
        mock_create_connection.return_value = None

        addon = MongoDBRoomsAddon()
        addon.config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )

        result = addon.initConnection()
        assert result is False
        assert addon.connection is None

    def test_init_connection_no_config(self):
        addon = MongoDBRoomsAddon()
        result = addon.initConnection()
        assert result is False

    def test_load_credentials_success(self):
        addon = MongoDBRoomsAddon()
        addon.config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )

        result = addon.loadCredentials(db_user="test_user", db_password="test_pass")
        assert result is True

    def test_load_credentials_missing(self):
        addon = MongoDBRoomsAddon()
        addon.config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )

        result = addon.loadCredentials(db_user="test_user")
        assert result is False

    @patch('mongodb_rooms_pkg.addon.create_collection')
    def test_create_collection_method(self, mock_create_collection):
        mock_response = MagicMock()
        mock_create_collection.return_value = mock_response

        addon = MongoDBRoomsAddon()
        addon.config = MagicMock()
        addon.connection = MagicMock()

        result = addon.create_collection("test_collection")
        assert result == mock_response
        mock_create_collection.assert_called_once()

    @patch('mongodb_rooms_pkg.addon.insert')
    def test_insert_method(self, mock_insert):
        mock_response = MagicMock()
        mock_insert.return_value = mock_response

        addon = MongoDBRoomsAddon()
        addon.config = MagicMock()
        addon.connection = MagicMock()

        result = addon.insert("test_collection", document={"test": "data"})
        assert result == mock_response
        mock_insert.assert_called_once()

    @patch('mongodb_rooms_pkg.addon.delete')
    def test_delete_method(self, mock_delete):
        mock_response = MagicMock()
        mock_delete.return_value = mock_response

        addon = MongoDBRoomsAddon()
        addon.config = MagicMock()
        addon.connection = MagicMock()

        result = addon.delete("test_collection", filter={"test": "data"})
        assert result == mock_response
        mock_delete.assert_called_once()

    def test_logger_properties(self):
        addon = MongoDBRoomsAddon()
        logger = addon.logger

        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert logger.addon_type == "storage"

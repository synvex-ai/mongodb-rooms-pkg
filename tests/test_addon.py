from unittest.mock import Mock, patch

import pytest

from mongodb_rooms_pkg.addon import MongoDBRoomsAddon


class TestMongoDBRoomsAddon:
    def test_addon_initialization(self):
        addon = MongoDBRoomsAddon()

        assert addon.type == "storage"
        assert addon.modules == ["actions", "configuration", "memory", "services", "storage", "tools", "utils"]
        assert addon.config is None
        assert addon.connection is None
        assert addon.credentials is not None

    def test_logger_property(self):
        addon = MongoDBRoomsAddon()
        logger = addon.logger

        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
        assert logger.addon_type == "storage"

    def test_load_addon_config_success(self):
        addon = MongoDBRoomsAddon()
        config_data = {
            "id": "test_id",
            "name": "test_name", 
            "description": "test_desc",
            "type": "storage",
            "host": "localhost",
            "database": "testdb",
            "secrets": {"db_user": "user", "db_password": "pass"}
        }

        with patch('mongodb_rooms_pkg.configuration.CustomAddonConfig') as MockConfig, \
             patch.object(addon, 'initConnection', return_value=True) as mock_init:
            mock_config_instance = Mock()
            MockConfig.return_value = mock_config_instance

            result = addon.loadAddonConfig(config_data)

            MockConfig.assert_called_once_with(**config_data)
            assert addon.config == mock_config_instance
            mock_init.assert_called_once()
            assert result is True

    def test_load_addon_config_failure(self):
        addon = MongoDBRoomsAddon()

        with patch('mongodb_rooms_pkg.configuration.CustomAddonConfig', side_effect=Exception("Config error")):
            result = addon.loadAddonConfig({})

            assert result is False

    def test_load_credentials_success(self):
        addon = MongoDBRoomsAddon()
        credentials = {"db_user": "user", "db_password": "pass"}

        with patch.object(addon.credentials, 'store_multiple') as mock_store:
            result = addon.loadCredentials(**credentials)

            mock_store.assert_called_once_with(credentials)
            assert result is True

    def test_load_credentials_failure(self):
        addon = MongoDBRoomsAddon()
        credentials = {"db_user": "user", "db_password": "pass"}

        with patch.object(addon.credentials, 'store_multiple', side_effect=Exception("Store error")):
            result = addon.loadCredentials(**credentials)

            assert result is False

    def test_init_connection_no_config(self):
        addon = MongoDBRoomsAddon()
        
        result = addon.initConnection()
        
        assert result is False

    def test_init_connection_success(self):
        addon = MongoDBRoomsAddon()
        mock_config = Mock()
        mock_config.scheme = "mongodb"
        addon.config = mock_config

        with patch('mongodb_rooms_pkg.addon.build_uri', return_value="mongodb://test") as mock_build_uri, \
             patch('mongodb_rooms_pkg.addon.create_connection', return_value=Mock()) as mock_create_conn:
            
            result = addon.initConnection()
            
            mock_build_uri.assert_called_once_with(mock_config)
            mock_create_conn.assert_called_once_with("mongodb://test")
            assert result is True

    def test_describe_action(self):
        addon = MongoDBRoomsAddon()
        
        with patch('mongodb_rooms_pkg.addon.describe', return_value={"status": "success"}) as mock_describe:
            result = addon.describe()
            
            mock_describe.assert_called_once_with(addon.config, addon.connection)
            assert result == {"status": "success"}

    def test_test_method_success(self):
        addon = MongoDBRoomsAddon()

        with patch('importlib.import_module') as mock_import:
            mock_module = Mock()
            mock_module.__all__ = ['TestComponent']
            mock_module.TestComponent = Mock()
            mock_import.return_value = mock_module

            result = addon.test()

            assert result is True

    def test_test_method_import_error(self):
        addon = MongoDBRoomsAddon()

        with patch('importlib.import_module', side_effect=ImportError("Module not found")):
            result = addon.test()

            assert result is False
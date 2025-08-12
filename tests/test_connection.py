import pytest
from unittest.mock import MagicMock, patch
from mongodb_rooms_pkg.services.connection import build_uri, create_connection
from mongodb_rooms_pkg.configuration.addonconfig import CustomAddonConfig


def get_base_config():
    return {
        "id": "test",
        "type": "mongodb",
        "name": "Test Config",
        "description": "Test configuration"
    }


class TestBuildUri:
    def test_basic_uri(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        expected = "mongodb://user:pass@localhost:27017/testdb?authSource=admin"
        assert uri == expected

    def test_srv_uri(self):
        config = CustomAddonConfig(
            **get_base_config(),
            scheme="mongodb+srv",
            host="cluster.mongodb.net",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        expected = "mongodb+srv://user:pass@cluster.mongodb.net/testdb?authSource=admin"
        assert uri == expected

    def test_uri_without_auth(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "", "db_password": ""}
        )
        uri = build_uri(config)
        expected = "mongodb://localhost:27017/testdb?authSource=admin"
        assert uri == expected

    def test_uri_with_custom_port(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            port=27018,
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        expected = "mongodb://user:pass@localhost:27018/testdb?authSource=admin"
        assert uri == expected

    def test_uri_with_tls(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            tls=True,
            tlsCAFile="/path/to/ca.pem",
            tlsCertificateKeyFile="/path/to/cert.pem",
            tlsAllowInvalidCertificates=True,
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "tls=true" in uri
        assert "tlsCAFile=%2Fpath%2Fto%2Fca.pem" in uri
        assert "tlsCertificateKeyFile=%2Fpath%2Fto%2Fcert.pem" in uri
        assert "tlsAllowInvalidCertificates=true" in uri

    def test_uri_with_replica_set(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            replicaSet="rs0",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "replicaSet=rs0" in uri

    def test_uri_with_read_preference(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            readPreference="secondary",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "readPreference=secondary" in uri

    def test_uri_with_read_preference_tags(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            readPreferenceTags=["dc:west", "use:reporting"],
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "readPreferenceTags%5B0%5D=dc%3Awest" in uri
        assert "readPreferenceTags%5B1%5D=use%3Areporting" in uri

    def test_uri_with_write_concern(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            w="majority",
            wtimeoutMS=5000,
            journal=True,
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "w=majority" in uri
        assert "wtimeoutMS=5000" in uri
        assert "journal=true" in uri

    def test_uri_with_connection_options(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            connectTimeoutMS=30000,
            socketTimeoutMS=0,
            serverSelectionTimeoutMS=30000,
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=300000,
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "connectTimeoutMS=30000" in uri
        assert "socketTimeoutMS=0" in uri
        assert "serverSelectionTimeoutMS=30000" in uri
        assert "maxPoolSize=100" in uri
        assert "minPoolSize=10" in uri
        assert "maxIdleTimeMS=300000" in uri

    def test_uri_with_compressors(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            compressors="zlib,snappy",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "compressors=zlib%2Csnappy" in uri

    def test_uri_with_app_name(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            appname="MyApp",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "appname=MyApp" in uri

    def test_uri_with_additional_options(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            options={"custom": "value", "another": "option"},
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "custom=value" in uri
        assert "another=option" in uri

    def test_uri_special_characters_encoding(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="test@db",
            secrets={"db_user": "user@domain", "db_password": "p@ss/word"}
        )
        uri = build_uri(config)
        assert "user%40domain:p%40ss%2Fword@" in uri
        assert "/test@db?" in uri

    def test_uri_none_values_excluded(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            authSource=None,
            replicaSet=None,
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "replicaSet" not in uri

    def test_uri_journal_false(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            journal=False,
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "journal=false" in uri

    def test_uri_no_database(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        uri = build_uri(config)
        assert "/?authSource=admin" in uri


class TestCreateConnection:
    @patch('mongodb_rooms_pkg.services.connection.MongoClient')
    def test_create_connection_success(self, mock_mongo_client):
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        uri = "mongodb://localhost:27017/testdb"
        result = create_connection(uri)
        
        assert result == mock_client
        mock_mongo_client.assert_called_once_with(uri, serverSelectionTimeoutMS=5000)
        mock_client.admin.command.assert_called_once_with("ping")

    @patch('mongodb_rooms_pkg.services.connection.MongoClient')
    def test_create_connection_failure(self, mock_mongo_client):
        from pymongo.errors import ConnectionFailure
        mock_mongo_client.side_effect = ConnectionFailure("Connection failed")
        
        uri = "mongodb://localhost:27017/testdb"
        result = create_connection(uri)
        
        assert result is None

    @patch('mongodb_rooms_pkg.services.connection.MongoClient')
    def test_create_connection_auth_error(self, mock_mongo_client):
        mock_mongo_client.side_effect = Exception("Authentication failed")
        
        uri = "mongodb://user:pass@localhost:27017/testdb"
        result = create_connection(uri)
        
        assert result is None

    @patch('mongodb_rooms_pkg.services.connection.MongoClient')
    def test_create_connection_invalid_uri_error(self, mock_mongo_client):
        mock_mongo_client.side_effect = Exception("Invalid URI format")
        
        uri = "invalid://localhost:27017/testdb"
        result = create_connection(uri)
        
        assert result is None

    @patch('mongodb_rooms_pkg.services.connection.MongoClient')
    def test_create_connection_generic_error(self, mock_mongo_client):
        mock_mongo_client.side_effect = ValueError("Some other error")
        
        uri = "mongodb://localhost:27017/testdb"
        result = create_connection(uri)
        
        assert result is None
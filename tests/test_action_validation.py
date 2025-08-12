import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from mongodb_rooms_pkg.actions.create_collection import ActionInput as CreateInput, ActionOutput as CreateOutput, create_collection
from mongodb_rooms_pkg.actions.insert import ActionInput as InsertInput, ActionOutput as InsertOutput, insert
from mongodb_rooms_pkg.configuration.addonconfig import CustomAddonConfig


def get_base_config():
    return {
        "id": "test",
        "type": "mongodb", 
        "name": "Test Config",
        "description": "Test configuration"
    }


class TestCreateCollectionValidation:
    def test_create_collection_input_valid(self):
        input_data = CreateInput(collection_name="test_collection")
        assert input_data.collection_name == "test_collection"
        assert input_data.schema_definition is None
        assert input_data.options is None

    def test_create_collection_input_with_schema(self):
        schema = {
            "bsonType": "object",
            "properties": {"name": {"bsonType": "string"}}
        }
        input_data = CreateInput(
            collection_name="test_collection",
            schema_definition=schema
        )
        assert input_data.collection_name == "test_collection"
        assert input_data.schema_definition == schema

    def test_create_collection_input_validation_error(self):
        with pytest.raises(ValidationError):
            CreateInput()

    def test_create_collection_output_structure(self):
        output = CreateOutput(
            collection_name="test",
            created=True,
            schema_applied=False,
            message="Success"
        )
        assert output.collection_name == "test"
        assert output.created is True
        assert output.schema_applied is False
        assert output.message == "Success"

    def test_create_collection_no_connection(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = CreateInput(collection_name="test_collection")
        
        response = create_collection(config, None, input_data)
        
        assert response.code == 500
        assert response.message == "No database connection provided"
        assert response.output.created is False

    def test_create_collection_existing_collection(self):
        mock_connection = MagicMock()
        mock_db = MagicMock()
        mock_connection.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = ["existing_collection"]
        
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = CreateInput(collection_name="existing_collection")
        
        response = create_collection(config, mock_connection, input_data)
        
        assert response.code == 409
        assert "already exists" in response.message
        assert response.output.created is False

    def test_create_collection_success(self):
        mock_connection = MagicMock()
        mock_db = MagicMock()
        mock_connection.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = []
        
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = CreateInput(collection_name="new_collection")
        
        response = create_collection(config, mock_connection, input_data)
        
        assert response.code == 201
        assert "Successfully created" in response.message
        assert response.output.created is True
        mock_db.create_collection.assert_called_once()

    def test_create_collection_with_schema(self):
        mock_connection = MagicMock()
        mock_db = MagicMock()
        mock_connection.__getitem__.return_value = mock_db
        mock_db.list_collection_names.return_value = []
        
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        schema = {"bsonType": "object", "properties": {"name": {"bsonType": "string"}}}
        input_data = CreateInput(
            collection_name="new_collection",
            schema_definition=schema
        )
        
        response = create_collection(config, mock_connection, input_data)
        
        assert response.code == 201
        assert response.output.schema_applied is True
        assert "with JSON schema validation" in response.message


class TestInsertValidation:
    def test_insert_input_single_document(self):
        input_data = InsertInput(
            collection="test_collection",
            document={"name": "test", "value": 123}
        )
        assert input_data.collection == "test_collection"
        assert input_data.document == {"name": "test", "value": 123}
        assert input_data.documents is None

    def test_insert_input_multiple_documents(self):
        docs = [{"name": "test1"}, {"name": "test2"}]
        input_data = InsertInput(
            collection="test_collection",
            documents=docs
        )
        assert input_data.collection == "test_collection"
        assert input_data.documents == docs
        assert input_data.document is None

    def test_insert_input_validation_error(self):
        with pytest.raises(ValidationError):
            InsertInput()

    def test_insert_output_structure(self):
        output = InsertOutput(
            collection_name="test",
            inserted_count=2,
            inserted_ids=["id1", "id2"],
            acknowledged=True
        )
        assert output.collection_name == "test"
        assert output.inserted_count == 2
        assert len(output.inserted_ids) == 2
        assert output.acknowledged is True

    def test_insert_no_connection(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = InsertInput(
            collection="test_collection",
            document={"test": "data"}
        )
        
        response = insert(config, None, input_data)
        
        assert response.code == 500
        assert response.message == "No database connection provided"
        assert response.output.inserted_count == 0

    def test_insert_no_document_or_documents(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = InsertInput(collection="test_collection")
        
        response = insert(config, MagicMock(), input_data)
        
        assert response.code == 400
        assert "Either 'document' or 'documents' must be provided" in response.message

    def test_insert_both_document_and_documents(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = InsertInput(
            collection="test_collection",
            document={"test": "data"},
            documents=[{"test": "data"}]
        )
        
        response = insert(config, MagicMock(), input_data)
        
        assert response.code == 400
        assert "Cannot provide both 'document' and 'documents'" in response.message

    def test_insert_single_document_success(self):
        mock_connection = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        
        mock_connection.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value = mock_result
        mock_result.inserted_id = "test_id"
        mock_result.acknowledged = True
        
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = InsertInput(
            collection="test_collection",
            document={"test": "data"}
        )
        
        response = insert(config, mock_connection, input_data)
        
        assert response.code == 200
        assert response.output.inserted_count == 1
        assert len(response.output.inserted_ids) == 1
        assert response.output.acknowledged is True
        mock_collection.insert_one.assert_called_once()

    def test_insert_multiple_documents_success(self):
        mock_connection = MagicMock()
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_result = MagicMock()
        
        mock_connection.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_many.return_value = mock_result
        mock_result.inserted_ids = ["id1", "id2"]
        mock_result.acknowledged = True
        
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = InsertInput(
            collection="test_collection",
            documents=[{"test": "data1"}, {"test": "data2"}]
        )
        
        response = insert(config, mock_connection, input_data)
        
        assert response.code == 200
        assert response.output.inserted_count == 2
        assert len(response.output.inserted_ids) == 2
        assert response.output.acknowledged is True
        mock_collection.insert_many.assert_called_once()
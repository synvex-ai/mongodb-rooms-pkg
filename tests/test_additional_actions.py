import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError
from mongodb_rooms_pkg.actions.delete import ActionInput as DeleteInput, ActionOutput as DeleteOutput, delete
from mongodb_rooms_pkg.actions.update import ActionInput as UpdateInput, ActionOutput as UpdateOutput, update
from mongodb_rooms_pkg.actions.upsert import ActionInput as UpsertInput, ActionOutput as UpsertOutput, upsert
from mongodb_rooms_pkg.actions.describe import ActionInput as DescribeInput, ActionOutput as DescribeOutput, describe
from mongodb_rooms_pkg.actions.describe_collection import ActionInput as DescribeCollInput, ActionOutput as DescribeCollOutput, describe_collection
from mongodb_rooms_pkg.configuration.addonconfig import CustomAddonConfig


def get_base_config():
    return {
        "id": "test",
        "type": "mongodb", 
        "name": "Test Config",
        "description": "Test configuration"
    }


class TestDeleteValidation:
    def test_delete_input_valid(self):
        input_data = DeleteInput(
            collection="test_collection",
            filter={"name": "test"}
        )
        assert input_data.collection == "test_collection"
        assert input_data.filter == {"name": "test"}

    def test_delete_input_validation_error(self):
        with pytest.raises(ValidationError):
            DeleteInput()

    def test_delete_output_structure(self):
        output = DeleteOutput(
            collection_name="test",
            deleted_count=5,
            acknowledged=True
        )
        assert output.collection_name == "test"
        assert output.deleted_count == 5
        assert output.acknowledged is True

    def test_delete_no_connection(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = DeleteInput(
            collection="test_collection",
            filter={"name": "test"}
        )
        
        response = delete(config, None, input_data)
        
        assert response.code == 500
        assert "No database connection provided" in response.message
        assert response.output.deleted_count == 0


class TestUpdateValidation:
    def test_update_input_valid(self):
        input_data = UpdateInput(
            collection="test_collection",
            filter={"name": "test"},
            update={"$set": {"value": 123}}
        )
        assert input_data.collection == "test_collection"
        assert input_data.filter == {"name": "test"}
        assert input_data.update == {"$set": {"value": 123}}

    def test_update_input_validation_error(self):
        with pytest.raises(ValidationError):
            UpdateInput()

    def test_update_output_structure(self):
        output = UpdateOutput(
            collection_name="test",
            matched_count=3,
            modified_count=2,
            acknowledged=True
        )
        assert output.collection_name == "test"
        assert output.matched_count == 3
        assert output.modified_count == 2
        assert output.acknowledged is True

    def test_update_no_connection(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = UpdateInput(
            collection="test_collection",
            filter={"name": "test"},
            update={"$set": {"value": 123}}
        )
        
        response = update(config, None, input_data)
        
        assert response.code == 500
        assert "No database connection provided" in response.message
        assert response.output.matched_count == 0


class TestUpsertValidation:
    def test_upsert_input_valid(self):
        input_data = UpsertInput(
            collection="test_collection",
            filter={"name": "test"},
            update={"$set": {"value": 123}}
        )
        assert input_data.collection == "test_collection"
        assert input_data.filter == {"name": "test"}
        assert input_data.update == {"$set": {"value": 123}}

    def test_upsert_input_validation_error(self):
        with pytest.raises(ValidationError):
            UpsertInput()

    def test_upsert_output_structure(self):
        output = UpsertOutput(
            collection_name="test",
            matched_count=1,
            modified_count=1,
            upserted_id=None,
            acknowledged=True,
            operation_performed="upsert"
        )
        assert output.collection_name == "test"
        assert output.matched_count == 1
        assert output.modified_count == 1
        assert output.upserted_id is None
        assert output.acknowledged is True
        assert output.operation_performed == "upsert"

    def test_upsert_no_connection(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        input_data = UpsertInput(
            collection="test_collection",
            filter={"name": "test"},
            update={"$set": {"value": 123}}
        )
        
        response = upsert(config, None, input_data)
        
        assert response.code == 500
        assert "No database connection provided" in response.message
        assert response.output.matched_count == 0


class TestDescribeValidation:
    def test_describe_input_valid(self):
        input_data = DescribeInput()
        assert isinstance(input_data, DescribeInput)

    def test_describe_output_structure(self):
        output = DescribeOutput(
            database_name="test_db",
            collections=["col1", "col2"],
            total_collections=2
        )
        assert output.database_name == "test_db"
        assert output.collections == ["col1", "col2"]
        assert output.total_collections == 2

    def test_describe_no_connection(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        
        response = describe(config, None)
        
        assert response.code == 500
        assert "No database connection provided" in response.message
        assert response.output.total_collections == 0


class TestDescribeCollectionValidation:
    def test_describe_collection_input_valid(self):
        input_data = DescribeCollInput(collection_names=["test_collection"])
        assert input_data.collection_names == ["test_collection"]

    def test_describe_collection_input_validation_error(self):
        with pytest.raises(ValidationError):
            DescribeCollInput()

    def test_describe_collection_output_structure(self):
        from mongodb_rooms_pkg.actions.describe_collection import CollectionDescription
        
        collection_desc = CollectionDescription(
            collection_name="test",
            exists=True
        )
        output = DescribeCollOutput(
            collections=[collection_desc],
            total_processed=1
        )
        assert len(output.collections) == 1
        assert output.collections[0].collection_name == "test"
        assert output.collections[0].exists is True
        assert output.total_processed == 1

    def test_describe_collection_no_collections(self):
        config = CustomAddonConfig(
            **get_base_config(),
            host="localhost",
            database="testdb",
            secrets={"db_user": "user", "db_password": "pass"}
        )
        
        response = describe_collection(config, None, [])
        
        assert response.code == 400
        assert "Collection names array is required" in response.message
        assert response.output.total_processed == 0
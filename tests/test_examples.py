import pytest
from unittest.mock import patch
from mongodb_rooms_pkg.memory.example import demo_memory
from mongodb_rooms_pkg.utils.example import demo_util
from mongodb_rooms_pkg.storage.example import demo_storage
from mongodb_rooms_pkg.tools.example import demo_tool


class TestDemoMemory:
    def test_demo_memory_return_value(self):
        result = demo_memory()
        assert isinstance(result, dict)
        assert result["memory_status"] == "active"
        assert result["entries"] == 0

    def test_demo_memory_structure(self):
        result = demo_memory()
        assert "memory_status" in result
        assert "entries" in result
        assert len(result) == 2

    @patch('mongodb_rooms_pkg.memory.example.logger')
    def test_demo_memory_logging(self, mock_logger):
        demo_memory()
        mock_logger.debug.assert_called_once_with(
            "Template rooms package - Demo memory system initialized successfully!"
        )


class TestDemoUtil:
    def test_demo_util_return_value(self):
        result = demo_util()
        assert isinstance(result, dict)
        assert result["utility"] == "helper"
        assert result["status"] == "ready"

    def test_demo_util_structure(self):
        result = demo_util()
        assert "utility" in result
        assert "status" in result
        assert len(result) == 2

    @patch('mongodb_rooms_pkg.utils.example.logger')
    def test_demo_util_logging(self, mock_logger):
        demo_util()
        mock_logger.debug.assert_called_once_with(
            "Template rooms package - Demo utility function executed successfully!"
        )


class TestDemoStorage:
    def test_demo_storage_return_value(self):
        result = demo_storage()
        assert isinstance(result, dict)
        assert result["service"] == "running"
        assert result["port"] == 8080

    def test_demo_storage_structure(self):
        result = demo_storage()
        assert "service" in result
        assert "port" in result
        assert len(result) == 2

    def test_demo_storage_port_type(self):
        result = demo_storage()
        assert isinstance(result["port"], int)

    @patch('mongodb_rooms_pkg.storage.example.logger')
    def test_demo_storage_logging(self, mock_logger):
        demo_storage()
        mock_logger.debug.assert_called_once_with(
            "Template rooms package - Demo storage started successfully!"
        )


class TestDemoTool:
    def test_demo_tool_return_value(self):
        result = demo_tool()
        assert isinstance(result, dict)
        assert result["tool"] == "template_tool"
        assert result["result"] == "success"

    def test_demo_tool_structure(self):
        result = demo_tool()
        assert "tool" in result
        assert "result" in result
        assert len(result) == 2

    @patch('mongodb_rooms_pkg.tools.example.logger')
    def test_demo_tool_logging(self, mock_logger):
        demo_tool()
        mock_logger.debug.assert_called_once_with(
            "Template rooms package - Demo tool executed successfully!"
        )


class TestAllExampleFunctions:
    def test_all_functions_return_dict(self):
        functions = [demo_memory, demo_util, demo_storage, demo_tool]
        for func in functions:
            result = func()
            assert isinstance(result, dict)
            assert len(result) == 2

    def test_all_functions_have_unique_content(self):
        results = [demo_memory(), demo_util(), demo_storage(), demo_tool()]
        
        # Check that all results are different
        for i in range(len(results)):
            for j in range(i + 1, len(results)):
                assert results[i] != results[j]
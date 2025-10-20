import pytest
from pydantic import ValidationError

from mongodb_rooms_pkg.actions.base import ActionResponse, OutputBase, TokensSchema


class TestTokensSchema:
    def test_valid_tokens_schema(self):
        tokens = TokensSchema(stepAmount=100, totalCurrentAmount=1000)
        assert tokens.stepAmount == 100
        assert tokens.totalCurrentAmount == 1000

    def test_tokens_schema_validation(self):
        with pytest.raises(ValidationError):
            TokensSchema(stepAmount="invalid", totalCurrentAmount=1000)

        with pytest.raises(ValidationError):
            TokensSchema(stepAmount=100, totalCurrentAmount="invalid")

    def test_tokens_schema_missing_fields(self):
        with pytest.raises(ValidationError):
            TokensSchema(stepAmount=100)

        with pytest.raises(ValidationError):
            TokensSchema(totalCurrentAmount=1000)

    def test_tokens_schema_negative_values(self):
        tokens = TokensSchema(stepAmount=-100, totalCurrentAmount=-1000)
        assert tokens.stepAmount == -100
        assert tokens.totalCurrentAmount == -1000

    def test_tokens_schema_zero_values(self):
        tokens = TokensSchema(stepAmount=0, totalCurrentAmount=0)
        assert tokens.stepAmount == 0
        assert tokens.totalCurrentAmount == 0


class TestOutputBase:
    def test_output_base_creation(self):
        output = OutputBase()
        assert isinstance(output, OutputBase)

    def test_output_base_inheritance(self):
        class CustomOutput(OutputBase):
            message: str
            count: int

        custom_output = CustomOutput(message="test", count=5)
        assert custom_output.message == "test"
        assert custom_output.count == 5
        assert isinstance(custom_output, OutputBase)


class TestActionResponse:
    def test_valid_action_response(self):
        tokens = TokensSchema(stepAmount=100, totalCurrentAmount=1000)
        output = OutputBase()

        response = ActionResponse(
            output=output,
            tokens=tokens,
            message="Success",
            code=200
        )

        assert response.output == output
        assert response.tokens == tokens
        assert response.message == "Success"
        assert response.code == 200

    def test_action_response_minimal(self):
        tokens = TokensSchema(stepAmount=100, totalCurrentAmount=1000)
        output = OutputBase()

        response = ActionResponse(output=output, tokens=tokens)

        assert response.output == output
        assert response.tokens == tokens
        assert response.message is None
        assert response.code is None

    def test_action_response_validation(self):
        with pytest.raises(ValidationError):
            ActionResponse(output=None, tokens=None)

    def test_action_response_with_custom_output(self):
        class CustomOutput(OutputBase):
            result: str
            success: bool

        tokens = TokensSchema(stepAmount=50, totalCurrentAmount=500)
        output = CustomOutput(result="completed", success=True)

        response = ActionResponse(
            output=output,
            tokens=tokens,
            message="Operation completed",
            code=201
        )

        assert response.output.result == "completed"
        assert response.output.success is True
        assert response.tokens.stepAmount == 50
        assert response.message == "Operation completed"
        assert response.code == 201

    def test_action_response_serialization(self):
        tokens = TokensSchema(stepAmount=100, totalCurrentAmount=1000)
        output = OutputBase()

        response = ActionResponse(
            output=output,
            tokens=tokens,
            message="Test message",
            code=200
        )

        response_dict = response.model_dump()

        assert "output" in response_dict
        assert "tokens" in response_dict
        assert response_dict["message"] == "Test message"
        assert response_dict["code"] == 200
        assert response_dict["tokens"]["stepAmount"] == 100
        assert response_dict["tokens"]["totalCurrentAmount"] == 1000

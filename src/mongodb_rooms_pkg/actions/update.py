from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel

from mongodb_rooms_pkg.configuration import CustomAddonConfig

from .base import ActionResponse, OutputBase, TokensSchema


class ActionInput(BaseModel):
    collection: str
    filter: dict[str, Any]
    update: dict[str, Any]
    update_many: Optional[bool] = False
    upsert: Optional[bool] = False

class ActionOutput(OutputBase):
    collection_name: str
    matched_count: int
    modified_count: int
    upserted_id: Optional[Any] = None
    acknowledged: bool

def update(config: CustomAddonConfig, connection, action_input: ActionInput) -> ActionResponse:
    logger.debug("MongoDB rooms package - Update action executing...")
    logger.debug(f"Config: {config}")
    logger.debug(f"Input: {action_input}")

    try:
        if not connection:
            tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
            message = "No database connection provided"
            code = 500
            output = ActionOutput(
                collection_name=action_input.collection,
                matched_count=0,
                modified_count=0,
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)

        if not action_input.filter:
            tokens = TokensSchema(stepAmount=300, totalCurrentAmount=16536)
            message = "Filter cannot be empty"
            code = 400
            output = ActionOutput(
                collection_name=action_input.collection,
                matched_count=0,
                modified_count=0,
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)

        if not action_input.update:
            tokens = TokensSchema(stepAmount=300, totalCurrentAmount=16536)
            message = "Update document cannot be empty"
            code = 400
            output = ActionOutput(
                collection_name=action_input.collection,
                matched_count=0,
                modified_count=0,
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)

        db = connection[config.database]
        collection = db[action_input.collection]

        if action_input.update_many:
            result = collection.update_many(
                action_input.filter,
                action_input.update,
                upsert=action_input.upsert
            )
        else:
            result = collection.update_one(
                action_input.filter,
                action_input.update,
                upsert=action_input.upsert
            )

        operation_type = "many" if action_input.update_many else "one"
        tokens = TokensSchema(stepAmount=1100, totalCurrentAmount=17336)
        message = f"Successfully updated {result.modified_count} document(s) in collection '{action_input.collection}' (update_{operation_type})"
        code = 200
        output = ActionOutput(
            collection_name=action_input.collection,
            matched_count=result.matched_count,
            modified_count=result.modified_count,
            upserted_id=getattr(result, 'upserted_id', None),
            acknowledged=result.acknowledged
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)

    except Exception as e:
        logger.error(f"Error updating documents: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error updating documents: {str(e)}"
        code = 500
        output = ActionOutput(
            collection_name=action_input.collection,
            matched_count=0,
            modified_count=0,
            acknowledged=False
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)

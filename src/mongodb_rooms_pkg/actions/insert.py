from typing import Any, Optional

from loguru import logger
from pydantic import BaseModel

from mongodb_rooms_pkg.configuration import CustomAddonConfig

from .base import ActionResponse, OutputBase, TokensSchema


class ActionInput(BaseModel):
    collection: str
    document: Optional[dict[str, Any]] = None
    documents: Optional[list[dict[str, Any]]] = None

class ActionOutput(OutputBase):
    collection_name: str
    inserted_count: int
    inserted_ids: list[Any]
    acknowledged: bool

def insert(config: CustomAddonConfig, connection, action_input: ActionInput) -> ActionResponse:
    logger.debug("MongoDB rooms package - Insert action executing...")
    logger.debug(f"Config: {config}")
    logger.debug(f"Input: {action_input}")

    try:
        if not connection:
            tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
            message = "No database connection provided"
            code = 500
            output = ActionOutput(
                collection_name=action_input.collection,
                inserted_count=0,
                inserted_ids=[],
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)

        if not action_input.document and not action_input.documents:
            tokens = TokensSchema(stepAmount=300, totalCurrentAmount=16536)
            message = "Either 'document' or 'documents' must be provided"
            code = 400
            output = ActionOutput(
                collection_name=action_input.collection,
                inserted_count=0,
                inserted_ids=[],
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)

        if action_input.document and action_input.documents:
            tokens = TokensSchema(stepAmount=300, totalCurrentAmount=16536)
            message = "Cannot provide both 'document' and 'documents'. Use one or the other"
            code = 400
            output = ActionOutput(
                collection_name=action_input.collection,
                inserted_count=0,
                inserted_ids=[],
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)

        db = connection[config.database]
        collection = db[action_input.collection]

        if action_input.document:
            result = collection.insert_one(action_input.document)
            inserted_ids = [result.inserted_id]
            inserted_count = 1
        else:
            result = collection.insert_many(action_input.documents)
            inserted_ids = result.inserted_ids
            inserted_count = len(inserted_ids)

        tokens = TokensSchema(stepAmount=1200, totalCurrentAmount=17436)
        message = f"Successfully inserted {inserted_count} document(s) into collection '{action_input.collection}'"
        code = 200
        output = ActionOutput(
            collection_name=action_input.collection,
            inserted_count=inserted_count,
            inserted_ids=inserted_ids,
            acknowledged=result.acknowledged
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)

    except Exception as e:
        logger.error(f"Error inserting documents: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error inserting documents: {str(e)}"
        code = 500
        output = ActionOutput(
            collection_name=action_input.collection,
            inserted_count=0,
            inserted_ids=[],
            acknowledged=False
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)

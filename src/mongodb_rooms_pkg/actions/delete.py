from loguru import logger
from typing import Optional, Dict, Any
from pydantic import BaseModel

from .base import ActionResponse, OutputBase, TokensSchema
from mongodb_rooms_pkg.configuration import CustomAddonConfig

class ActionInput(BaseModel):
    collection: str
    filter: Dict[str, Any]
    delete_many: Optional[bool] = False
    
class ActionOutput(OutputBase):
    collection_name: str
    deleted_count: int
    acknowledged: bool

def delete(config: CustomAddonConfig, connection, action_input: ActionInput) -> ActionResponse:
    logger.debug("MongoDB rooms package - Delete action executing...")
    logger.debug(f"Config: {config}")
    logger.debug(f"Input: {action_input}")
    
    try:
        if not connection:
            tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
            message = "No database connection provided"
            code = 500
            output = ActionOutput(
                collection_name=action_input.collection,
                deleted_count=0,
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        if not action_input.filter:
            tokens = TokensSchema(stepAmount=300, totalCurrentAmount=16536)
            message = "Filter cannot be empty for safety reasons"
            code = 400
            output = ActionOutput(
                collection_name=action_input.collection,
                deleted_count=0,
                acknowledged=False
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        db = connection[config.database]
        collection = db[action_input.collection]
        
        if action_input.delete_many:
            result = collection.delete_many(action_input.filter)
        else:
            result = collection.delete_one(action_input.filter)
        
        operation_type = "many" if action_input.delete_many else "one"
        tokens = TokensSchema(stepAmount=1000, totalCurrentAmount=17236)
        message = f"Successfully deleted {result.deleted_count} document(s) from collection '{action_input.collection}' (delete_{operation_type})"
        code = 200
        output = ActionOutput(
            collection_name=action_input.collection,
            deleted_count=result.deleted_count,
            acknowledged=result.acknowledged
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
    except Exception as e:
        logger.error(f"Error deleting documents: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error deleting documents: {str(e)}"
        code = 500
        output = ActionOutput(
            collection_name=action_input.collection,
            deleted_count=0,
            acknowledged=False
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
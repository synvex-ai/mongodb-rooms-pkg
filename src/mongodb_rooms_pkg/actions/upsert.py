from loguru import logger
from typing import Optional, Dict, Any
from pydantic import BaseModel

from .base import ActionResponse, OutputBase, TokensSchema
from mongodb_rooms_pkg.configuration import CustomAddonConfig

class ActionInput(BaseModel):
    collection: str
    filter: Dict[str, Any]
    update: Dict[str, Any]
    update_many: Optional[bool] = False
    
class ActionOutput(OutputBase):
    collection_name: str
    matched_count: int
    modified_count: int
    upserted_id: Optional[Any] = None
    acknowledged: bool
    operation_performed: str

def upsert(config: CustomAddonConfig, connection, action_input: ActionInput) -> ActionResponse:
    logger.debug("MongoDB rooms package - Upsert action executing...")
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
                acknowledged=False,
                operation_performed="none"
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
                acknowledged=False,
                operation_performed="none"
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
                acknowledged=False,
                operation_performed="none"
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        db = connection[config.database]
        collection = db[action_input.collection]
        
        if action_input.update_many:
            result = collection.update_many(
                action_input.filter, 
                action_input.update,
                upsert=True
            )
            operation_type = "update_many"
        else:
            result = collection.update_one(
                action_input.filter, 
                action_input.update,
                upsert=True
            )
            operation_type = "update_one"
        
        operation_performed = "insert" if result.upserted_id else "update"
        
        tokens = TokensSchema(stepAmount=1100, totalCurrentAmount=17336)
        message = f"Successfully performed upsert operation ({operation_performed}) in collection '{action_input.collection}' using {operation_type}"
        code = 200
        output = ActionOutput(
            collection_name=action_input.collection,
            matched_count=result.matched_count,
            modified_count=result.modified_count,
            upserted_id=getattr(result, 'upserted_id', None),
            acknowledged=result.acknowledged,
            operation_performed=operation_performed
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
    except Exception as e:
        logger.error(f"Error performing upsert operation: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error performing upsert operation: {str(e)}"
        code = 500
        output = ActionOutput(
            collection_name=action_input.collection,
            matched_count=0,
            modified_count=0,
            acknowledged=False,
            operation_performed="error"
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
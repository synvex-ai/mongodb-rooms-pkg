from loguru import logger
from typing import Optional, Dict, Any
from pydantic import BaseModel

from .base import ActionResponse, OutputBase, TokensSchema
from mongodb_rooms_pkg.configuration import CustomAddonConfig

class ActionInput(BaseModel):
    collection_name: str
    schema_definition: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    
class ActionOutput(OutputBase):
    collection_name: str
    created: bool
    schema_applied: bool
    message: str

def create_collection(config: CustomAddonConfig, connection, action_input: ActionInput) -> ActionResponse:
    logger.debug("MongoDB rooms package - Create collection action executing...")
    logger.debug(f"Config: {config}")
    logger.debug(f"Input: {action_input}")
    
    try:
        if not connection:
            tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
            message = "No database connection provided"
            code = 500
            output = ActionOutput(
                collection_name=action_input.collection_name,
                created=False,
                schema_applied=False,
                message="No database connection"
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        db = connection[config.database]
        existing_collections = db.list_collection_names()
        
        if action_input.collection_name in existing_collections:
            tokens = TokensSchema(stepAmount=300, totalCurrentAmount=16536)
            message = f"Collection '{action_input.collection_name}' already exists"
            code = 409
            output = ActionOutput(
                collection_name=action_input.collection_name,
                created=False,
                schema_applied=False,
                message="Collection already exists"
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        collection_options = action_input.options or {}
        
        if action_input.schema_definition:
            collection_options["validator"] = {
                "$jsonSchema": action_input.schema_definition
            }
            collection_options["validationLevel"] = collection_options.get("validationLevel", "strict")
            collection_options["validationAction"] = collection_options.get("validationAction", "error")
        
        db.create_collection(action_input.collection_name, **collection_options)
        
        schema_applied = bool(action_input.schema_definition)
        tokens = TokensSchema(stepAmount=1000, totalCurrentAmount=17236)
        message = f"Successfully created collection '{action_input.collection_name}'"
        if schema_applied:
            message += " with JSON schema validation"
        code = 201
        
        output = ActionOutput(
            collection_name=action_input.collection_name,
            created=True,
            schema_applied=schema_applied,
            message="Collection created successfully"
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
    except Exception as e:
        logger.error(f"Error creating collection: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error creating collection: {str(e)}"
        code = 500
        output = ActionOutput(
            collection_name=action_input.collection_name,
            created=False,
            schema_applied=False,
            message=f"Error: {str(e)}"
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
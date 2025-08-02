from loguru import logger
from typing import Optional
from pydantic import BaseModel

from .base import ActionResponse, OutputBase, TokensSchema
from mongodb_rooms_pkg.configuration import CustomAddonConfig

class ActionInput(BaseModel):
    pass
    
class ActionOutput(OutputBase):
    data: Optional[dict] = None

def describe(config: CustomAddonConfig) -> ActionResponse:
    logger.debug("MongoDB rooms package - Example action executed successfully!")
    logger.debug(f"Config: {config}")
    
    # decsribe bdd here
    
    tokens = TokensSchema(stepAmount=2000, totalCurrentAmount=16236)
    message = "Action executed successfully"
    code = 200
    output = ActionOutput(data={""})
    return ActionResponse(output=output, tokens=tokens, message=message, code=code)
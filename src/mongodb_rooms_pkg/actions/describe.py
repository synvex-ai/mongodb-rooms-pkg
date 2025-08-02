from loguru import logger
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from .base import ActionResponse, OutputBase, TokensSchema
from mongodb_rooms_pkg.configuration import CustomAddonConfig

class ActionInput(BaseModel):
    pass
    
class DatabaseStats(BaseModel):
    name: str
    size_on_disk: int
    empty: bool
    
class ActionOutput(OutputBase):
    database_name: str
    collections: List[str]
    database_stats: Optional[DatabaseStats] = None
    server_info: Optional[Dict[str, Any]] = None
    total_collections: int

def describe(config: CustomAddonConfig, connection) -> ActionResponse:
    logger.debug("MongoDB rooms package - Describe action executing...")
    logger.debug(f"Config: {config}")
    
    try:
        if not connection:
            tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
            message = "No database connection provided"
            code = 500
            output = ActionOutput(
                database_name="unknown",
                collections=[],
                total_collections=0
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        db = connection[config.database]
        
        collections = db.list_collection_names()
        
        db_stats = None
        server_info = None
        try:
            stats_result = db.command("dbStats")
            db_stats = DatabaseStats(
                name=stats_result.get("db", config.database),
                size_on_disk=stats_result.get("storageSize", 0),
                empty=stats_result.get("empty", True)
            )
        except Exception as e:
            logger.warning(f"Could not retrieve database stats: {e}")
        
        try:
            server_info = connection.server_info()
        except Exception as e:
            logger.warning(f"Could not retrieve server info: {e}")
        
        tokens = TokensSchema(stepAmount=1000, totalCurrentAmount=17236)
        message = f"Database '{config.database}' described successfully"
        code = 200
        output = ActionOutput(
            database_name=config.database,
            collections=collections,
            database_stats=db_stats,
            server_info=server_info,
            total_collections=len(collections)
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
    except Exception as e:
        logger.error(f"Error describing database: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error describing database: {str(e)}"
        code = 500
        output = ActionOutput(
            database_name=config.database,
            collections=[],
            total_collections=0
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
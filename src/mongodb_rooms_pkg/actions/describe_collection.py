from loguru import logger
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from .base import ActionResponse, OutputBase, TokensSchema
from mongodb_rooms_pkg.configuration import CustomAddonConfig

class ActionInput(BaseModel):
    collection_names: List[str]
    
class CollectionStats(BaseModel):
    count: int
    size: int
    avg_obj_size: Optional[float] = None
    storage_size: int
    indexes: int
    total_index_size: int
    
class FieldInfo(BaseModel):
    field_name: str
    data_types: List[str]
    null_count: int
    sample_values: List[Any]
    
class CollectionDescription(BaseModel):
    collection_name: str
    exists: bool
    stats: Optional[CollectionStats] = None
    indexes: Optional[List[Dict[str, Any]]] = None
    schema_sample: Optional[List[FieldInfo]] = None
    
class ActionOutput(OutputBase):
    collections: List[CollectionDescription]
    total_processed: int

def describe_collection(config: CustomAddonConfig, connection, collections: List[str] = None) -> ActionResponse:
    logger.debug("MongoDB rooms package - Describe collection action executing...")
    logger.debug(f"Config: {config}")
    logger.debug(f"Collection names: {collections}")
    
    if not collections:
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = "Collection names array is required"
        code = 400
        output = ActionOutput(
            collections=[],
            total_processed=0
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
    
    try:
        if not connection:
            tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
            message = "No database connection provided"
            code = 500
            output = ActionOutput(
                collections=[],
                total_processed=0
            )
            return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
        db = connection[config.database]
        existing_collections = db.list_collection_names()
        
        collection_descriptions = []
        
        for collection_name in collections:
            try:
                exists = collection_name in existing_collections
                
                if not exists:
                    collection_descriptions.append(CollectionDescription(
                        collection_name=collection_name,
                        exists=False
                    ))
                    continue
                
                collection = db[collection_name]
                stats = None
                indexes = None
                schema_sample = None
                
                try:
                    stats_result = db.command("collStats", collection_name)
                    stats = CollectionStats(
                        count=stats_result.get("count", 0),
                        size=stats_result.get("size", 0),
                        avg_obj_size=stats_result.get("avgObjSize"),
                        storage_size=stats_result.get("storageSize", 0),
                        indexes=stats_result.get("nindexes", 0),
                        total_index_size=stats_result.get("totalIndexSize", 0)
                    )
                except Exception as e:
                    logger.warning(f"Could not retrieve stats for {collection_name}: {e}")
                
                try:
                    indexes = list(collection.list_indexes())
                except Exception as e:
                    logger.warning(f"Could not retrieve indexes for {collection_name}: {e}")
                
                try:
                    sample_docs = list(collection.aggregate([
                        {"$sample": {"size": 10}}
                    ]))
                    
                    if sample_docs:
                        field_analysis = {}
                        for doc in sample_docs:
                            for field, value in doc.items():
                                if field not in field_analysis:
                                    field_analysis[field] = {
                                        "types": set(),
                                        "null_count": 0,
                                        "sample_values": []
                                    }
                                
                                if value is None:
                                    field_analysis[field]["null_count"] += 1
                                else:
                                    field_analysis[field]["types"].add(type(value).__name__)
                                    if len(field_analysis[field]["sample_values"]) < 3:
                                        field_analysis[field]["sample_values"].append(value)
                        
                        schema_sample = [
                            FieldInfo(
                                field_name=field,
                                data_types=list(info["types"]),
                                null_count=info["null_count"],
                                sample_values=info["sample_values"]
                            )
                            for field, info in field_analysis.items()
                        ]
                except Exception as e:
                    logger.warning(f"Could not analyze schema for {collection_name}: {e}")
                
                collection_descriptions.append(CollectionDescription(
                    collection_name=collection_name,
                    exists=True,
                    stats=stats,
                    indexes=indexes,
                    schema_sample=schema_sample
                ))
                
            except Exception as e:
                logger.error(f"Error processing collection {collection_name}: {e}")
                collection_descriptions.append(CollectionDescription(
                    collection_name=collection_name,
                    exists=False
                ))
        
        tokens = TokensSchema(stepAmount=1500 * len(collections), totalCurrentAmount=16236 + (1500 * len(collections)))
        message = f"Described {len(collections)} collections successfully"
        code = 200
        output = ActionOutput(
            collections=collection_descriptions,
            total_processed=len(collections)
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
        
    except Exception as e:
        logger.error(f"Error describing collections: {e}")
        tokens = TokensSchema(stepAmount=500, totalCurrentAmount=16236)
        message = f"Error describing collections: {str(e)}"
        code = 500
        output = ActionOutput(
            collections=[],
            total_processed=0
        )
        return ActionResponse(output=output, tokens=tokens, message=message, code=code)
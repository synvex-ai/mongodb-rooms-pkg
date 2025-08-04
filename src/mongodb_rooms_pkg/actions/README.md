# MongoDB Actions

## describe
**Input:** None
```json
{
    "action": "storage-mongo-1::describe"
}
```
**Output:** Database info, collections list, stats

## describe_collection  
**Input:** `collections` (array of collection names)
```json
{
    "action": "storage-mongo-1::describe_collection",
    "parameters": {
        "collections": ["users", "orders"]
    }
}
```
**Output:** Collection details, schema, indexes, stats

## insert
**Input:** `collection`, `document` OR `documents`
```json
{
    "action": "storage-mongo-1::insert",
    "parameters": {
        "collection": "users",
        "document": {"name": "John", "email": "john@example.com"}
    }
}
```
**Output:** Inserted count, inserted IDs

## update
**Input:** `collection`, `filter`, `update`, `update_many` (optional), `upsert` (optional)
```json
{
    "action": "storage-mongo-1::update",
    "parameters": {
        "collection": "users",
        "filter": {"user_id": "123"},
        "update": {"$set": {"status": "active"}},
        "update_many": false
    }
}
```
**Output:** Matched/modified counts, upserted ID

## upsert
**Input:** `collection`, `filter`, `update`, `update_many` (optional)
```json
{
    "action": "storage-mongo-1::upsert",
    "parameters": {
        "collection": "users",
        "filter": {"user_id": "123"},
        "update": {"$set": {"status": "active"}}
    }
}
```
**Output:** Matched/modified counts, operation type, upserted ID

## delete
**Input:** `collection`, `filter`, `delete_many` (optional)
```json
{
    "action": "storage-mongo-1::delete",
    "parameters": {
        "collection": "users",
        "filter": {"user_id": "123"},
        "delete_many": false
    }
}
```
**Output:** Deleted count

## create_collection
**Input:** `collection_name`, `schema_definition` (optional), `options` (optional)
```json
{
    "action": "storage-mongo-1::create_collection",
    "parameters": {
        "collection_name": "users",
        "schema_definition": {
            "type": "object",
            "required": ["user_id", "email"],
            "properties": {
                "user_id": {"type": "string"},
                "email": {"type": "string"}
            }
        }
    }
}
```
**Output:** Created status, schema applied status
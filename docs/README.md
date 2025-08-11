# MongoDB - AI Rooms Workflow Addon

## Overview

MongoDB database integration addon for Rooms AI, providing comprehensive database operations, schema management, and CRUD functionality.

**Addon Type:** `mongodb` (storage-type addon)

## Features

- **Database Operations**: Full MongoDB database and collection management
- **CRUD Operations**: Create, read, update, delete documents with flexible querying
- **Schema Management**: Collection creation with schema validation support  
- **Connection Management**: Advanced MongoDB connection with replica sets, TLS, and authentication
- **Tool Integration**: All actions available as tools for AI agent workflows
- **Comprehensive Configuration**: Support for MongoDB Atlas, replica sets, and advanced options

## Add to Rooms AI using poetry

Using the script

```bash
poetry add git+https://github.com/synvex-ai/mongodb-rooms-pkg.git
```

In the web interface, follow online guide for adding an addon. You can still use JSON in web interface.


## Configuration

### Addon Configuration
Add this addon to your AI Rooms workflow configuration:

```json
{
  "addons": [
    {
      "id": "mongo-db",
      "type": "mongodb",
      "name": "MongoDB Database",
      "enabled": true,
      "config": {
        "scheme": "mongodb",
        "host": "localhost",
        "port": 27017,
        "database": "myapp_db",
        "authSource": "admin"
      },
      "secrets": {
        "db_user": "MONGODB_USER",
        "db_password": "MONGODB_PASSWORD"
      }
    }
  ]
}
```

### Configuration Fields

#### BaseAddonConfig Fields
All addons inherit these base configuration fields:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | Yes | - | Unique identifier for the addon instance |
| `type` | string | Yes | - | Type of the addon ("mongodb") |
| `name` | string | Yes | - | Display name of the addon |
| `description` | string | Yes | - | Description of the addon |
| `enabled` | boolean | No | true | Whether the addon is enabled |

#### CustomAddonConfig Fields (mongodb-specific)
This MongoDB addon supports extensive configuration options:

**Core Connection:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `scheme` | string | No | "mongodb" | Connection scheme: "mongodb" or "mongodb+srv" |
| `host` | string | Yes | - | Database host or comma-separated replica set members |
| `port` | integer | No | 27017 | Database port (not used with mongodb+srv) |
| `database` | string | Yes | - | Default database name |

**Authentication:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `authSource` | string | No | "admin" | Authentication database |
| `authMechanism` | string | No | null | Auth mechanism (SCRAM-SHA-1, MONGODB-X509, GSSAPI) |

**Replica Set & TLS:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `replicaSet` | string | No | null | Name of the replica set |
| `tls` | boolean | No | null | Enable TLS/SSL |
| `tlsCAFile` | string | No | null | Path to Certificate Authority file |
| `tlsCertificateKeyFile` | string | No | null | Client certificate/key PEM file |
| `tlsAllowInvalidCertificates` | boolean | No | false | Allow invalid TLS certificates |

**Performance & Timeouts:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `connectTimeoutMS` | integer | No | null | Connection timeout in milliseconds |
| `socketTimeoutMS` | integer | No | null | Socket timeout in milliseconds |
| `serverSelectionTimeoutMS` | integer | No | null | Server selection timeout in milliseconds |
| `maxPoolSize` | integer | No | null | Maximum connections in connection pool |
| `minPoolSize` | integer | No | null | Minimum connections in connection pool |
| `maxIdleTimeMS` | integer | No | null | Maximum idle time for connections |

**Write Concern & Journaling:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `w` | string | No | null | Write concern (1, majority, etc.) |
| `wtimeoutMS` | integer | No | null | Timeout for write concern |
| `journal` | boolean | No | null | Wait for journal commit acknowledgement |

**Read Preferences:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `readPreference` | string | No | null | Read preference (primary, secondary, etc.) |
| `readPreferenceTags` | array | No | null | List of read preference tags |

**Additional Options:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `compressors` | string | No | null | Comma-separated compressors (zlib,snappy) |
| `appname` | string | No | null | Application name for MongoDB logs |
| `options` | object | No | null | Additional URI options as key-value pairs |

### Required Secrets

| Secret Key | Environment Variable | Description |
|------------|---------------------|-------------|
| `db_user` | `MONGODB_USER` | MongoDB username for authentication |
| `db_password` | `MONGODB_PASSWORD` | MongoDB password for authentication |

### Environment Variables
Create a `.env` file in your workflow directory:

```bash
# .env file
MONGODB_USER=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
```

## Available Actions

### `describe`
Get comprehensive information about the MongoDB database including collections, stats, and server info.

**Parameters:**
- No parameters required

**Output Structure:**
- `database_name` (string): Name of the connected database
- `collections` (array): List of collection names  
- `total_collections` (integer): Total number of collections
- `database_stats` (object): Database statistics and size information
- `server_info` (object): MongoDB server information

**Workflow Usage:**
```json
{
  "id": "get-db-info",
  "name": "Get Database Information",
  "action": "mongo-db::describe"
}
```

### `describe_collection`
Get detailed information about specific MongoDB collections including schema, indexes, and statistics.

**Parameters:**
- `collections` (array, required): Array of collection names to describe

**Output Structure:**
- `collections_info` (array): Detailed information for each collection
- `total_collections_described` (integer): Number of collections described

**Workflow Usage:**
```json
{
  "id": "describe-collections",
  "name": "Describe User Collections",
  "action": "mongo-db::describe_collection",
  "parameters": {
    "collections": ["users", "orders"]
  }
}
```

### `insert`
Insert single document or multiple documents into a MongoDB collection.

**Parameters:**
- `collection` (string, required): Collection name
- `document` (object, optional): Single document to insert
- `documents` (array, optional): Multiple documents to insert
- Note: Either `document` OR `documents` must be provided, not both

**Output Structure:**
- `collection_name` (string): Target collection name
- `inserted_count` (integer): Number of documents inserted
- `inserted_ids` (array): IDs of inserted documents
- `acknowledged` (boolean): Whether the operation was acknowledged

**Workflow Usage:**
```json
{
  "id": "add-user",
  "name": "Insert New User",
  "action": "mongo-db::insert",
  "parameters": {
    "collection": "users",
    "document": {"name": "John", "email": "john@example.com"}
  }
}
```

### `update`
Update documents in a MongoDB collection with flexible filtering and update options.

**Parameters:**
- `collection` (string, required): Collection name
- `filter` (object, required): Query filter to match documents
- `update` (object, required): Update operations to apply
- `update_many` (boolean, optional): Update multiple documents (default: false)
- `upsert` (boolean, optional): Create document if not found (default: false)

**Workflow Usage:**
```json
{
  "id": "update-user-status", 
  "name": "Update User Status",
  "action": "mongo-db::update",
  "parameters": {
    "collection": "users",
    "filter": {"user_id": "123"},
    "update": {"$set": {"status": "active"}},
    "update_many": false
  }
}
```

### `upsert`
Insert or update documents in a MongoDB collection (dedicated upsert operation).

**Parameters:**
- `collection` (string, required): Collection name
- `filter` (object, required): Query filter to match documents
- `update` (object, required): Data to insert or update using MongoDB update operators
- `update_many` (boolean, optional): Affect multiple documents (default: false)

**Workflow Usage:**
```json
{
  "id": "upsert-user-profile",
  "name": "Upsert User Profile",
  "action": "mongo-db::upsert",
  "parameters": {
    "collection": "users",
    "filter": {"user_id": "123"},
    "update": {"$set": {"status": "active"}}
  }
}
```

### `delete`
Delete documents from a MongoDB collection with flexible filtering options.

**Parameters:**
- `collection` (string, required): Collection name
- `filter` (object, required): Query filter to match documents to delete
- `delete_many` (boolean, optional): Delete multiple documents (default: false)

**Workflow Usage:**
```json
{
  "id": "remove-inactive-users",
  "name": "Delete Inactive Users",
  "action": "mongo-db::delete",
  "parameters": {
    "collection": "users",
    "filter": {"user_id": "123"},
    "delete_many": false
  }
}
```

### `create_collection`
Create a new MongoDB collection with optional schema validation and configuration options.

**Parameters:**
- `collection_name` (string, required): Name of the collection to create
- `schema_definition` (object, optional): JSON schema for document validation
- `options` (object, optional): Collection creation options

**Workflow Usage:**
```json
{
  "id": "create-users-collection",
  "name": "Create Users Collection", 
  "action": "mongo-db::create_collection",
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

## Usage Examples

### Basic Database Operations
```json
{
  "addons": [
    {
      "id": "mongo-db",
      "type": "mongodb",
      "name": "MongoDB Database",
      "enabled": true,
      "config": {
        "scheme": "mongodb",
        "host": "localhost",
        "port": 27017,
        "database": "myapp_db"
      },
      "secrets": {
        "db_user": "MONGODB_USER",
        "db_password": "MONGODB_PASSWORD"
      }
    }
  ],
  "entrypoints": [
    {
      "id": "default",
      "name": "Database Operations Workflow",
      "startAt": "get-db-info"
    }
  ],
  "workflow": {
    "id": "mongodb-operations",
    "name": "MongoDB Operations",
    "version": "1.0.0",
    "steps": [
      {
        "id": "get-db-info",
        "name": "Get Database Information",
        "action": "mongo-db::describe",
        "next": ["create-user"]
      },
      {
        "id": "create-user",
        "name": "Create New User",
        "action": "mongo-db::insert",
        "parameters": {
          "collection": "users",
          "document": {
            "name": "{{payload.user_name}}",
            "email": "{{payload.user_email}}",
            "created_at": "{{now}}"
          }
        },
        "next": ["update-user"]
      },
      {
        "id": "update-user",
        "name": "Update User Status",
        "action": "mongo-db::update",
        "parameters": {
          "collection": "users",
          "filter": {"email": "{{payload.user_email}}"},
          "update": {"$set": {"status": "active", "updated_at": "{{now}}"}}
        }
      }
    ]
  }
}
```

### MongoDB Atlas Configuration
```json
{
  "addons": [
    {
      "id": "mongo-atlas",
      "type": "mongodb",
      "name": "MongoDB Atlas",
      "enabled": true,
      "config": {
        "scheme": "mongodb+srv",
        "host": "cluster0.example.mongodb.net",
        "database": "production_db",
        "authSource": "admin",
        "tls": true,
        "maxPoolSize": 10,
        "w": "majority"
      },
      "secrets": {
        "db_user": "ATLAS_USER",
        "db_password": "ATLAS_PASSWORD"
      }
    }
  ]
}
```


## Testing & Lint

Like all Rooms AI deployments, addons should be roughly tested.

A basic PyTest is setup with a cicd to require 90% coverage in tests. Else it will not deploy the new release.

We also have ruff set up in cicd.

### Running the Tests

```bash
poetry run pytest tests/ --cov=src/mongodb_rooms_pkg --cov-report=term-missing
```

### Running the linter

```bash
poetry run ruff check . --fix
```

### Pull Requests & versioning

Like for all deployments, we use semantic versioning in cicd to automatize the versions.

For this, use the apprioriate commit message syntax for semantic release in github.


## Developers / Mainteners

- Adrien EPPLING :  [adrienesofts@gmail.com](mailto:adrienesofts@gmail.com)

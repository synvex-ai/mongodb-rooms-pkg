from pydantic import Field, model_validator
from typing import Optional, List, Dict
from .baseconfig import BaseAddonConfig


class CustomAddonConfig(BaseAddonConfig):
    scheme: str = Field("mongodb", description="Connection scheme, either 'mongodb' or 'mongodb+srv'")
    host: str = Field(..., description="Database host or comma-separated replica set members")
    port: Optional[int] = Field(27017, description="Database port (not used with 'mongodb+srv')")
    database: str = Field(..., description="Default database name to connect to")
    
    # Optionnal auth parameters
    authSource: Optional[str] = Field("admin", description="Authentication database")
    authMechanism: Optional[str] = Field(None, description="Authentication mechanism (e.g. SCRAM-SHA-1, MONGODB-X509, GSSAPI)")

    # Replica set & TLS/SSL
    replicaSet: Optional[str] = Field(None, description="Name of the replica set")
    tls: Optional[bool] = Field(None, description="Enable TLS/SSL")
    tlsCAFile: Optional[str] = Field(None, description="Path to Certificate Authority file")
    tlsCertificateKeyFile: Optional[str] = Field(None, description="Client certificate/key PEM file")
    tlsAllowInvalidCertificates: Optional[bool] = Field(False, description="Allow invalid TLS certificates")

    # Optional performance & behavior tuning
    connectTimeoutMS: Optional[int] = Field(None, description="Connection timeout in milliseconds")
    socketTimeoutMS: Optional[int] = Field(None, description="Socket timeout in milliseconds")
    serverSelectionTimeoutMS: Optional[int] = Field(None, description="Server selection timeout in milliseconds")
    maxPoolSize: Optional[int] = Field(None, description="Maximum number of connections in the connection pool")
    minPoolSize: Optional[int] = Field(None, description="Minimum number of connections in the connection pool")
    maxIdleTimeMS: Optional[int] = Field(None, description="Maximum idle time for connections")
    
    # Write concern & journaling
    w: Optional[str] = Field(None, description="Write concern (e.g. 1, majority)")
    wtimeoutMS: Optional[int] = Field(None, description="Timeout for write concern")
    journal: Optional[bool] = Field(None, description="Whether to wait for journal commit acknowledgement")

    # Read preferences
    readPreference: Optional[str] = Field(None, description="Read preference (e.g. primary, secondary)")
    readPreferenceTags: Optional[List[str]] = Field(None, description="List of read preference tags")

    compressors: Optional[str] = Field(None, description="Comma-separated list of compressors (e.g. zlib,snappy)")
    appname: Optional[str] = Field(None, description="Name of the application connecting to MongoDB")
    options: Optional[Dict[str, str]] = Field(None, description="Additional URI options as key-value pairs")

    @model_validator(mode='after')
    def validate_db_secrets(self):
        required_secrets = ["db_password", "db_user"]
        missing = [s for s in required_secrets if s not in self.secrets]
        if missing and not (self.username and self.password):
            raise ValueError(f"Missing database secrets: {missing}")
        return self

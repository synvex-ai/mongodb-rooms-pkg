from loguru import logger
from mongodb_rooms_pkg.configuration.addonconfig import CustomAddonConfig
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional

from urllib.parse import quote_plus


def build_uri(config: "CustomAddonConfig") -> str:
    """
    Build a MongoDB URI from the given configuration.
    """
    scheme = config.scheme or "mongodb"
    is_srv = scheme == "mongodb+srv"
    user = config.secrets.get("db_user")
    password = config.secrets.get("db_password")
    auth_part = ""
    if user and password:
        auth_part = f"{quote_plus(user)}:{quote_plus(password)}@"
    if is_srv:
        host_part = config.host
    else:
        host_part = config.host
        if config.port:
            host_part += f":{config.port}"
    database = config.database or ""
    query_params = {
        "authSource": config.authSource,
        "authMechanism": config.authMechanism,
        "replicaSet": config.replicaSet,
        "tls": str(config.tls).lower() if config.tls is not None else None,
        "tlsCAFile": config.tlsCAFile,
        "tlsCertificateKeyFile": config.tlsCertificateKeyFile,
        "tlsAllowInvalidCertificates": str(config.tlsAllowInvalidCertificates).lower()
        if config.tlsAllowInvalidCertificates is not None else None,
        "connectTimeoutMS": config.connectTimeoutMS,
        "socketTimeoutMS": config.socketTimeoutMS,
        "serverSelectionTimeoutMS": config.serverSelectionTimeoutMS,
        "maxPoolSize": config.maxPoolSize,
        "minPoolSize": config.minPoolSize,
        "maxIdleTimeMS": config.maxIdleTimeMS,
        "w": config.w,
        "wtimeoutMS": config.wtimeoutMS,
        "journal": str(config.journal).lower() if config.journal is not None else None,
        "readPreference": config.readPreference,
        "appname": config.appname,
        "compressors": config.compressors,
    }
    if config.readPreferenceTags:
        for i, tag in enumerate(config.readPreferenceTags):
            query_params[f"readPreferenceTags[{i}]"] = tag
    if config.options:
        query_params.update(config.options)
    # Remove unset params
    query = "&".join(
        f"{quote_plus(str(k))}={quote_plus(str(v))}"
        for k, v in query_params.items()
        if v is not None
    )
    uri = f"{scheme}://{auth_part}{host_part}/{database}"
    if query:
        uri += f"?{query}"
    return uri

def create_connection(uri: str) -> Optional[MongoClient]:
    """
    Create a MongoDB connection using the provided URI.
    Returns a MongoClient if successful, otherwise None.
    """
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logger.info("Successfully connected to MongoDB.")
        return client
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None
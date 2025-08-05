import importlib
from loguru import logger
from .actions.describe import describe
from .actions.describe_collection import describe_collection
from .actions.create_collection import create_collection
from .actions.insert import insert
from .actions.delete import delete
from .actions.upsert import upsert
from .services.credentials import CredentialsRegistry
from mongodb_rooms_pkg.services.connection import build_uri, create_connection


class MongoDBRoomsAddon:
    """
    Template Rooms Package Addon Class
    
    This class provides access to all template rooms package functionality
    and can be instantiated by external programs using this package.
    """
    
    type = "storage"
    
    def __init__(self):
        self.modules = ["actions", "configuration", "memory", "services", "storage", "tools", "utils"]
        self.config = None
        self.connection = None
        self.credentials = CredentialsRegistry()

    @property
    def logger(self):
        """Custom logger that prefixes all messages with addon type"""
        class PrefixedLogger:
            def __init__(self, addon_type):
                self.addon_type = addon_type
                self._logger = logger
            
            def debug(self, message):
                self._logger.debug(f"[TYPE: {self.addon_type.upper()}] {message}")
            
            def info(self, message):
                self._logger.info(f"[TYPE: {self.addon_type.upper()}] {message}")
            
            def warning(self, message):
                self._logger.warning(f"[TYPE: {self.addon_type.upper()}] {message}")
            
            def error(self, message):
                self._logger.error(f"[TYPE: {self.addon_type.upper()}] {message}")
        
        return PrefixedLogger(self.type)

    def describe(self) -> dict:
        self.logger.info("Describing MongoDB Rooms Addon...")
        return describe(self.config, self.connection)
    
    def describe_collection(self, collections: list) -> dict:
        self.logger.info(f"Describing collections: {collections}")
        return describe_collection(self.config, self.connection, collections)
    
    def create_collection(self, collection_name: str, schema_definition: dict = None, options: dict = None) -> dict:
        from .actions.create_collection import ActionInput
        action_input = ActionInput(collection_name=collection_name, schema_definition=schema_definition, options=options)
        self.logger.info(f"Creating collection: {collection_name}")
        return create_collection(self.config, self.connection, action_input)
    
    def insert(self, collection: str, document: dict = None, documents: list = None) -> dict:
        from .actions.insert import ActionInput
        action_input = ActionInput(collection=collection, document=document, documents=documents)
        self.logger.info(f"Inserting into collection: {collection}")
        return insert(self.config, self.connection, action_input)
    
    def update(self, collection: str, filter: dict, update_data: dict, update_many: bool = False, upsert: bool = False) -> dict:
        from .actions.update import ActionInput, update
        action_input = ActionInput(collection=collection, filter=filter, update=update_data, update_many=update_many, upsert=upsert)
        self.logger.info(f"Updating collection: {collection}")
        return update(self.config, self.connection, action_input)
    
    def delete(self, collection: str, filter: dict, delete_many: bool = False) -> dict:
        from .actions.delete import ActionInput
        action_input = ActionInput(collection=collection, filter=filter, delete_many=delete_many)
        self.logger.info(f"Deleting from collection: {collection}")
        return delete(self.config, self.connection, action_input)
    
    def upsert(self, collection: str, filter: dict, update_data: dict, update_many: bool = False) -> dict:
        from .actions.upsert import ActionInput
        action_input = ActionInput(collection=collection, filter=filter, update=update_data, update_many=update_many)
        self.logger.info(f"Upserting into collection: {collection}")
        return upsert(self.config, self.connection, action_input)

    def initConnection(self) -> bool:
        """
        Initialize connection with the provided configuration.
        Returns:
            bool: True if connection is initialized successfully, False otherwise
        """
        if not self.config or not hasattr(self.config, 'scheme'):
            self.logger.error("No valid configuration found. Cannot initialize connection.")
            return False
            
        self.logger.info("Initializing connection with provided configuration...")
        try:
            uri = build_uri(self.config)
            self.logger.debug(f"Connection URI for MongoDB: {uri}")
            self.connection = create_connection(uri)
            if self.connection is None:
                self.logger.error("MongoDB client connection failed.")
                return False
            self.logger.info("Connection initialized successfully for MongoDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize connection for MongoDB: {e}")
            return False

    def test(self) -> bool:
        """
        Test function for template rooms package.
        Tests each module and reports available components.
        Test connections with credentials if required.
        
        Returns:
            bool: True if test passes, False otherwise
        """
        self.logger.info(f"Running {self.__class__.__name__} test...")

        total_components = 0
        for module_name in self.modules:
            try:
                module = importlib.import_module(f"mongodb_rooms_pkg.{module_name}")
                components = getattr(module, '__all__', [])
                component_count = len(components)
                total_components += component_count
                for component_name in components:
                    self.logger.info(f"Processing component: {component_name}")
                    if hasattr(module, component_name):
                        component = getattr(module, component_name)
                        self.logger.info(f"Component {component_name} type: {type(component)}")
                        if callable(component):
                            try:
                                skip_instantiation = False
                                try:
                                    from pydantic import BaseModel
                                    if hasattr(component, '__bases__') and any(
                                        issubclass(base, BaseModel) for base in component.__bases__ if isinstance(base, type)
                                    ):
                                        self.logger.info(f"Component {component_name} is a Pydantic model, skipping instantiation")
                                        skip_instantiation = True
                                except (ImportError, TypeError):
                                    pass
                                # skip models require parameters
                                if component_name in ['ActionInput', 'ActionOutput', 'ActionResponse', 'OutputBase', 'TokensSchema']:
                                    self.logger.info(f"Component {component_name} requires parameters, skipping instantiation")
                                    skip_instantiation = True
                                
                                if not skip_instantiation:
                                    # result = component()
                                    self.logger.info(f"Component {component_name}() would be executed successfully")
                                else:
                                    self.logger.info(f"Component {component_name} exists and is valid (skipped instantiation)")
                            except Exception as e:
                                self.logger.warning(f"Component {component_name}() failed: {e}")
                                self.logger.error(f"Exception details for {component_name}: {str(e)}")
                                raise e
                self.logger.info(f"{component_count} {module_name} loaded correctly, available imports: {', '.join(components)}")
            except ImportError as e:
                self.logger.error(f"Failed to import {module_name}: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Error testing {module_name}: {e}")
                return False
        self.logger.info("Template rooms package test completed successfully!")
        self.logger.info(f"Total components loaded: {total_components} across {len(self.modules)} modules")
        return True
    
    def loadAddonConfig(self, addon_config: dict):
        """
        Load addon configuration.
        
        Args:
            addon_config (dict): Addon configuration dictionary
        
        Returns:
            bool: True if configuration is loaded successfully, False otherwise
        """
        try:
            from mongodb_rooms_pkg.configuration import CustomAddonConfig
            
            self.logger.debug(f"Received addon_config: {addon_config}")
            
            config_data = addon_config.copy()
            if 'config' in addon_config and isinstance(addon_config['config'], dict):
                config_data.update(addon_config['config'])
                self.logger.debug(f"Merged config_data: {config_data}")
            
            self.config = CustomAddonConfig(**config_data)
            self.logger.info(f"Addon configuration loaded successfully: {self.config}")
            
            connection_success = self.initConnection()
            if not connection_success:
                self.logger.error("Connection initialization failed after loading configuration")
                return False
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to load addon configuration: {e}")
            return False

    def loadCredentials(self, **kwargs) -> bool:
        """
        Load credentials and store them in the credentials registry.
        Takes individual secrets as keyword arguments for validation.
        
        Args:
            **kwargs: Individual credential key-value pairs
        
        Returns:
            bool: True if credentials are loaded successfully, False otherwise
        """
        self.logger.debug("Loading credentials...")
        self.logger.debug(f"Received credentials: {kwargs}")
        try:
            if self.config and hasattr(self.config, 'secrets'):
                required_secrets = list(self.config.secrets.keys())
                missing_secrets = [secret for secret in required_secrets if secret not in kwargs]
                if missing_secrets:
                    raise ValueError(f"Missing required secrets: {missing_secrets}")
            
            self.credentials.store_multiple(kwargs)
            self.logger.info(f"Loaded {len(kwargs)} credentials successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return False
"""
RedisClient for managing Redis connections and operations.

This module provides a singleton RedisClient class that connects to a Redis server.

It uses environment variables to configure the connection parameters, including host, port, and password.
If Redis is disabled or unavailable, a mock client is used instead.

Environment Variables:
- REDIS_INSTANCE_HOSTNAME: The hostname of the Redis server.
- REDIS_INSTANCE_PORT: The port of the Redis server.
- REDIS_INSTANCE_SECRET: The password for the Redis server (if required).
- REDIS_TLS_ENABLED: Whether to use TLS (default: True). This is optional.
- REDIS_DISABLED: Whether to disable Redis (default: False). This is optional

Note: We have an abstraction here for get and set. If we decide to use lists or sets in the future, we can add those methods here as well.

"""

import os
import redis
import json
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

logger = logging.getLogger(__name__)

class MockRedisClient:
    """
    A mock Redis client that logs operations but does nothing.
    Used when Redis is disabled or unavailable.
    """
    def __init__(self, reason="Redis is disabled"):
        self.reason = reason
        logger.error(f"Using MockRedisClient: {reason}")
        
    def set_with_expiry(self, key, value, expiry_seconds=3600):
        logger.info(f"Mock Redis: Would set key '{key}' and value '{value}' (expiry: {expiry_seconds}s) - {self.reason}")
        return True

    def delete(self, key):
        logger.info(f"Mock Redis: Would delete key '{key}' - {self.reason}")
        return True

    def keys(self, pattern="*"):
        logger.info(f"Mock Redis: Would get keys with pattern '{pattern}' - {self.reason}")
        return []

    def get(self, key):
        logger.info(f"Mock Redis: Would get key '{key}' - {self.reason}")
        return None
        
    def shutdown(self):
        logger.info("Mock Redis: Shutdown called - no action needed")
        return True

class RedisClient:
    _instance = None
    _last_error = None
    
    @classmethod
    def get_instance(cls):
        """
        Retrieve the singleton instance of RedisClient.
        If Redis is disabled or unavailable, a mock client will be returned.
        """
        if cls._instance is None:
            cls._instance = RedisClient()
        return cls._instance
    
    def __init__(self):
        """
        Initialize the RedisClient with connection parameters from environment variables.
        If Redis is disabled or unavailable, a mock client will be used.
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # Check if Redis is explicitly disabled
        redis_disabled = os.getenv("REDIS_DISABLED", "False").lower() in ("true", "1", "t", "yes")
        if redis_disabled:
            self._use_mock_client("Redis is disabled via REDIS_DISABLED env var. Set to 'False' to enable Redis.")
            return
            
        # Get Redis connection details from environment variables
        redis_host = os.getenv("REDIS_INSTANCE_HOSTNAME")
        redis_port = os.getenv("REDIS_INSTANCE_PORT")
        redis_password = os.getenv("REDIS_INSTANCE_SECRET")
        
        # Check if TLS should be enabled (default to True if not specified)
        redis_tls_enabled = os.getenv("REDIS_TLS_ENABLED", "True").lower() in ("true", "1", "t", "yes")
        
        # Validate essential environment variables
        if not all([redis_host, redis_port]):
            error_msg = "Redis host and port environment variables must be provided."
            self._use_mock_client(error_msg)
            return
        
        try:
            # Create Redis client with or without password
            connection_params = {
                "host": redis_host,
                "port": int(redis_port),
                "decode_responses": True
            }
            
            # Add password if provided
            if redis_password:
                connection_params["password"] = redis_password
                # Username is required when using password authentication with Azure Redis
                connection_params["username"] = "default"
                
            # Add SSL/TLS if enabled
            if redis_tls_enabled:
                connection_params["ssl"] = True
                
            self._redis = redis.Redis(**connection_params)
                
            # Test connection
            self._redis.ping()
            logger.info("RedisClient initialized successfully.")
            self._initialized = True
            self._using_mock = False
        except Exception as e:
            RedisClient._last_error = str(e)
            self._use_mock_client(f"Redis connection failed: {e}")

    def _use_mock_client(self, reason):
        """
        Set up a mock client with the given reason.
        """
        self._mock = MockRedisClient(reason)
        self._initialized = True
        self._using_mock = True

    def get_last_error(self):
        """
        Return the last error that occurred when trying to connect to Redis.
        """
        return RedisClient._last_error
        
    def shutdown(self):
        """
        Close the Redis connection if it exists.
        """
        if not self._using_mock and hasattr(self, '_redis') and self._redis:
            self._redis.close()
            logger.info("RedisClient shutdown completed.")
        return True

    def set_with_expiry(self, key, value, expiry_seconds=3600):
        """
        Set a value in Redis with an expiration time.
        
        Args:
            key (str): The key to set
            value (any): The value to set
            expiry_seconds (int): The expiration time in seconds (default: 1 hour)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self._using_mock:
            return self._mock.set_with_expiry(key, value, expiry_seconds)
            
        try:
            serialized_value = json.dumps(value)
            success = self._redis.setex(key, expiry_seconds, serialized_value)
            if success:
                logger.debug(f"Successfully set Redis key: {key}")
            return success
        except Exception as e:
            logger.warning(f"Failed to set Redis key {key}: {e}")
            return False

    def delete(self, key):
        """
        Delete a key from Redis.

        Args:
            key (str): The key to delete.

        Returns:
            bool: True if successful, False otherwise.
        """
        if self._using_mock:
            return self._mock.delete(key)

        try:
            success = self._redis.delete(key)
            if success:
                logger.debug(f"Successfully deleted Redis key: {key}")
            return success
        except Exception as e:
            logger.warning(f"Failed to delete Redis key {key}: {e}")
            return False

    def keys(self, pattern="*"):
        """
        Get all keys matching the given pattern from Redis.

        Args:
            pattern (str): The pattern to match keys (default: "*")

        Returns:
            list: A list of matching keys, or an empty list if none found
        """
        if self._using_mock:
            return self._mock.keys(pattern)

        try:
            keys = self._redis.keys(pattern)
            logger.debug(f"Successfully retrieved Redis keys: {keys}")
            return keys
        except Exception as e:
            logger.warning(f"Failed to get Redis keys: {e}")
            return []

    def get(self, key):
        """
        Get a value from Redis.
        
        Args:
            key (str): The key to get
            
        Returns:
            any: The value if successful, None otherwise
        """
        if self._using_mock:
            return self._mock.get(key)
            
        try:
            result = self._redis.get(key)
            if result:
                logger.debug(f"Successfully retrieved Redis key: {key}")
                return json.loads(result)
            return None
        except Exception as e:
            logger.warning(f"Failed to get Redis key {key}: {e}")
            return None

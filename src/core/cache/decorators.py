"""
Redis cache decorators for caching function results.

This module provides decorators for caching function results in Redis with different scoping strategies:
- cache_platform: Caches results globally across the platform
- cache_platform_with_args: Caches results globally with dynamic keys based on function arguments
- cache_user: Caches results per user

It also provides utilities for cache invalidation:
- invalidate_platform_cache: Invalidate platform-level cache entries
- invalidate_user_cache: Invalidate user-level cache entries
"""

import logging
from functools import wraps
from typing import Any, Callable

from src.clients.redis import RedisClient
from src.core.context.vars import ms_user_object_id_var

logger = logging.getLogger(__name__)


def _build_platform_key(key: str) -> str:
    """
    Build a platform-specific cache key.
    
    Args:
        key (str): The base key
        
    Returns:
        str: The formatted platform key
    """
    return f"lambots:api:platform:{key}"


def _build_user_key(key: str) -> str:
    """
    Build a user-specific cache key using the current user's ID from context.
    
    Args:
        key (str): The base key
        
    Returns:
        str: The formatted user key
        
    Raises:
        ValueError: If user ID is not available in context
    """
    user_id = ms_user_object_id_var.get()
    if not user_id:
        raise ValueError("User ID not available in context. Ensure user is authenticated.")
    return f"lambots:api:user:{user_id}:{key}"


def _convert_result_if_needed(result: Any, return_type: type = None) -> Any:
    """
    Convert result to specified type if provided and result is a dictionary.
    
    Args:
        result: The result to potentially convert
        return_type: The class type to convert to
        
    Returns:
        The converted result or original result if no conversion needed
    """
    if return_type is not None and isinstance(result, dict):
        return return_type(**result)
    return result


def _serialize_result_for_cache(result: Any, return_type: type = None) -> Any:
    """
    This handles the case of pydantic and also generic classes.
    Serialize result for caching. If return_type is specified and result has a dict() method,
    serialize it to a dictionary for JSON compatibility.
    
    Args:
        result: The result to potentially serialize
        return_type: The class type hint (indicates if serialization is needed)
        

    Returns:
        The serialized result (dict) or original result if no serialization needed
    """
    if return_type is not None and hasattr(result, 'model_dump') and callable(getattr(result, 'model_dump')):
        return result.model_dump()
    elif return_type is not None and hasattr(result, '__dict__') and callable(getattr(result, '__dict__')):
        return result.__dict__
    return result


def cache_platform(key: str, ttl: int = 3600, return_type: type = None):
    """
    Decorator for caching function results at the platform level.
    
    Args:
        key (str): The cache key to use
        ttl (int): Time to live in seconds (default: 1 hour)
        return_type (type, optional): Class type to convert dictionary results to
        
    Usage:
        @cache_platform("api_config", 1800)
        def get_api_config():
            return {"setting": "value"}
            
        @cache_platform("language_model", 3600, LanguageModelConfig)
        def get_language_model():
            return {"name": "model1", "display_name": "Model 1"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            redis_client = RedisClient.get_instance()
            cache_key = _build_platform_key(key)
            
            # Try to get from cache first
            cached_result = redis_client.get(cache_key)
            if cached_result is not None:
                return _convert_result_if_needed(cached_result, return_type)
            
            # Execute function and get result
            result = func(*args, **kwargs)
            if result is not None:
                # Serialize result for caching (convert objects to dicts if needed)
                serialized_result = _serialize_result_for_cache(result, return_type)
                redis_client.set_with_expiry(cache_key, serialized_result, ttl)
            
            # Return the original result (no conversion needed as function returns correct type)
            return result
        return wrapper
    return decorator


def cache_user(key: str, ttl: int = 900, return_type: type = None):
    """
    Decorator for caching function results at the user level.
    
    Args:
        key (str): The cache key to use
        ttl (int): Time to live in seconds (default: 15 minutes)
        return_type (type, optional): Class type to convert dictionary results to
        
    Usage:
        @cache_user("user_preferences", 1800)
        def get_user_preferences():
            return {"theme": "dark", "language": "en"}
            
        @cache_user("user_config", 1800, LamBotConfig)
        def get_user_config():
            return {"setting": "value"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            redis_client = RedisClient.get_instance()
            
            # Early return if user context is not available
            try:
                cache_key = _build_user_key(key)
            except ValueError as e:
                logger.warning(f"Unable to build user cache key: {e}")
                return func(*args, **kwargs)
            
            # Try to get from cache first
            cached_result = redis_client.get(cache_key)
            if cached_result is not None:
                return _convert_result_if_needed(cached_result, return_type)
            
            # Execute function and get result
            result = func(*args, **kwargs)
            if result is not None:
                # Serialize result for caching (convert objects to dicts if needed)
                serialized_result = _serialize_result_for_cache(result, return_type)
                redis_client.set_with_expiry(cache_key, serialized_result, ttl)
            
            # Return the original result (no conversion needed as function returns correct type)
            return result
        return wrapper
    return decorator


def cache_platform_with_args(key_template: str, ttl: int = 3600, return_type: type = None):
    """
    Decorator for caching function results at the platform level with dynamic keys based on function arguments.
    
    Args:
        key_template (str): The cache key template using {arg_name} placeholders for function arguments
        ttl (int): Time to live in seconds (default: 1 hour)
        return_type (type, optional): Class type to convert dictionary results to
        
    Usage:
        @cache_platform_with_args("user_config:{user_id}", 1800)
        def get_user_config(user_id: str):
            return {"setting": "value"}
            
        @cache_platform_with_args("language_model:{language_model_name}", 3600, LanguageModelConfig)
        def fetch_language_model(self, language_model_name: str):
            return model_data
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import inspect
            
            redis_client = RedisClient.get_instance()
            
            # Get function signature to map args to parameter names
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Build cache key by formatting template with arguments
            # Skip 'self' argument if it exists (for instance methods)
            format_args = {k: v for k, v in bound_args.arguments.items() if k != 'self'}
            
            # Early return if cache key template is invalid
            try:
                cache_key_suffix = key_template.format(**format_args)
                cache_key = _build_platform_key(cache_key_suffix)
            except KeyError as e:
                logger.warning(f"Cache key template missing argument: {e}. Executing function without caching.")
                return func(*args, **kwargs)
            
            # Try to get from cache first
            cached_result = redis_client.get(cache_key)
            if cached_result is not None:
                return _convert_result_if_needed(cached_result, return_type)
            
            # Execute function and get result
            result = func(*args, **kwargs)
            if result is not None:
                # Serialize result for caching (convert objects to dicts if needed)
                serialized_result = _serialize_result_for_cache(result, return_type)
                redis_client.set_with_expiry(cache_key, serialized_result, ttl)
            
            # Return the original result (no conversion needed as function returns correct type)
            return result
        return wrapper
    return decorator


def invalidate_platform_cache(patterns: list = None, keys: list = None):
    """
    Invalidate cached entries for platform-level cache.
    
    Args:
        patterns (list, optional): List of key patterns to match (e.g., ["language_model:*"])
        keys (list, optional): List of specific cache keys to invalidate (e.g., ["all_language_models"])
        
    Usage:
        # Invalidate specific keys
        invalidate_platform_cache(keys=["all_language_models", "language_model_keys"])
        
        # Invalidate by pattern
        invalidate_platform_cache(patterns=["language_model:*"])
        
        # Invalidate both
        invalidate_platform_cache(
            keys=["all_language_models"], 
            patterns=["language_model:*"]
        )
    """
    redis_client = RedisClient.get_instance()
    
    # Invalidate specific keys
    if keys:
        for key in keys:
            cache_key = _build_platform_key(key)
            redis_client.delete(cache_key)
    
    # Invalidate by patterns
    if patterns:
        for pattern in patterns:
            full_pattern = _build_platform_key(pattern)
            matching_keys = redis_client.keys(full_pattern)
            for key in matching_keys:
                redis_client.delete(key)


def invalidate_user_cache(patterns: list = None, keys: list = None):
    """
    Invalidate cached entries for user-level cache.
    
    Args:
        patterns (list, optional): List of key patterns to match
        keys (list, optional): List of specific cache keys to invalidate
    """
    redis_client = RedisClient.get_instance()
    
    # Invalidate specific keys
    if keys:
        for key in keys:
            try:
                cache_key = _build_user_key(key)
                redis_client.delete(cache_key)
            except ValueError:
                logger.warning(f"Unable to build user cache key for: {key}")
    
    # Invalidate by patterns
    if patterns:
        for pattern in patterns:
            try:
                full_pattern = _build_user_key(pattern)
                matching_keys = redis_client.keys(full_pattern)
                for key in matching_keys:
                    redis_client.delete(key)
            except ValueError:
                logger.warning(f"Unable to build user cache pattern for: {pattern}")

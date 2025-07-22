from aiocache import caches
from aiocache.serializers import JsonSerializer
from .config import settings

caches.set_config({
    'default': {
        'cache': "aiocache.RedisCache",
        'endpoint': settings.cache_host,
        'port': settings.cache_port,
        'password': settings.cache_password,
        'ttl': settings.cache_ttl_seconds,
        'serializer': {'class': "aiocache.serializers.JsonSerializer"}
    }
})

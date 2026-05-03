from environs import Env

env = Env()

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (
                    env.str("REDIS_HOST", "127.0.0.1"),
                    env.int("REDIS_PORT", 6379),
                )
            ],
            "capacity": 1500,
            "expiry": 10,
        },
    },
}

REDIS_URL = (
    f"redis://{env.str('REDIS_HOST', '127.0.0.1')}:{env.int('REDIS_PORT', 6379)}/0"
)

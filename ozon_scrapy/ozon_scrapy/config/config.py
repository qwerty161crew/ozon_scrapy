from pydantic_settings import BaseSettings


class RabbitMqSettings(BaseSettings):
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"


class Config(BaseSettings):
    rabbit_mq: RabbitMqSettings

    @classmethod
    def create(cls):
        return cls(rabbit_mq=RabbitMqSettings())

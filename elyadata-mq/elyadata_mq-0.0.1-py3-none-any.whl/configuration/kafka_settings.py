from pydantic import BaseSettings, Field


class KafkaSettings(BaseSettings):
    KAFKA_DEFAULT_ENCODING: str = Field(default="UTF-8",
                                        description="Default encoding/decoding")

    KAFKA_DEFAULT_TIMEOUT: int = Field(default=5,
                                       description="Default consumer timeout")

    KAFKA_NUM_MESSAGES: int = Field(default=1,
                                    description="Default number of messages to be consumed")

    KAFKA_AUTO_OFFSET_RESET: str = Field(default="earliest",
                                         description="Default auto offset reset")

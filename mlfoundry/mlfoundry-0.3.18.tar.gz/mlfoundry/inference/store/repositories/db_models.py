from sqlalchemy import JSON, BigInteger, Column, DateTime, Index, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class InferenceLog(Base):
    __tablename__ = "mlfoundry_inference_log"
    # https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#allowing-autoincrement-behavior-sqlalchemy-types-other-than-integer-integer
    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    # Identifying the model
    model_name = Column(String(256), nullable=False)
    model_version = Column(String(64), nullable=False)
    # identifying the inference payload
    inference_id = Column(String(36), nullable=False)
    features = Column(JSON, nullable=False)
    predictions = Column(JSON, nullable=False)
    occurred_at = Column(DateTime(), nullable=False)

    raw_data = Column(JSON)
    actuals = Column(JSON)

    __table_args__ = (
        Index(
            "mlfoundry_inference_log_model_name_inference_id",
            "model_name",
            "inference_id",
        ),
    )

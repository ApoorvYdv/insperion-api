from sqlalchemy import JSON, Boolean, Integer, MetaData, Text
from sqlalchemy.orm import Mapped, mapped_column

from insperion_api.core.models import Base


class ConfigBase(Base):
    __abstract__ = True
    metadata = MetaData(schema="config")


class Config(ConfigBase):
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    config_section: Mapped[str] = mapped_column(Text, nullable=False)
    config_key: Mapped[str] = mapped_column(Text, nullable=False)
    config_value: Mapped[dict] = mapped_column(JSON, nullable=True)
    config_description: Mapped[str] = mapped_column(Text, nullable=True)
    is_exposable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

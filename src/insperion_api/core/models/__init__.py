from datetime import UTC, date, datetime, time
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def time_now():
    return datetime.now(UTC)


def current_user():
    return "user_name"  # TODO


class Base(DeclarativeBase):
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_on: Mapped[str] = mapped_column(
        DateTime(timezone=True), default=time_now, nullable=False
    )
    created_by: Mapped[str] = mapped_column(
        String(64), default=current_user, nullable=True
    )
    modified_on: Mapped[str] = mapped_column(
        DateTime(timezone=True), default=time_now, onupdate=time_now, nullable=False
    )
    modified_by: Mapped[str] = mapped_column(
        String(64), default=current_user, onupdate=current_user, nullable=True
    )

    def to_dict(self):
        def convert_value(value):
            if isinstance(value, Base):
                return value.to_dict()
            elif isinstance(value, dict):
                return {key: convert_value(val) for key, val in value.items()}
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            elif isinstance(value, datetime):
                return value.strftime("%m-%d-%Y %H:%M:%S")
            elif isinstance(value, date):
                return value.strftime("%m-%d-%Y")
            elif isinstance(value, time):
                return value.strftime("%H:%M:%S")
            elif isinstance(value, Decimal):
                return float(value)
            elif hasattr(value, "to_dict"):
                return convert_value(value.to_dict())
            elif hasattr(value, "__dict__"):
                return convert_value(vars(value))
            return value

        return {
            key: convert_value(value)
            for key, value in self.__dict__.items()
            if not key.startswith(
                "_"
            )  # Exclude private or SQLAlchemy internal attributes
        }

    @classmethod
    def column_names(cls):
        return {c_attr.key for c_attr in inspect(cls).column_attrs}  # type: ignore

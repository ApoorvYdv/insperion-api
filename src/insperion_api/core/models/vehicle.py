from typing import List, Optional

from sqlalchemy import JSON, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from insperion_api.core.models import Base


class VehicleBase(Base):
    __abstract__ = True

    metadata = MetaData(schema="vehicle")


class VehicleBrand(VehicleBase):
    __tablename__ = "vehicle_brand"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    country: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    established_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)

    # Relationships
    models: Mapped[List["VehicleModel"]] = relationship(
        "VehicleModel", back_populates="brand"
    )


class VehicleModel(VehicleBase):
    __tablename__ = "vehicle_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brand.id"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    year_launched: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    body_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    seating_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    brand: Mapped["VehicleBrand"] = relationship("Brand", back_populates="models")
    variants: Mapped[List["VehicleVariant"]] = relationship(
        "VehicleVariant", back_populates="model"
    )


class VehicleVariant(VehicleBase):
    __tablename__ = "vehicle_variant"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_model.id"), nullable=False
    )
    variant_name: Mapped[str] = mapped_column(String(256), nullable=False)
    engine_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    transmission: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    fuel_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    vin: Mapped[str] = mapped_column(String(128), nullable=True)
    psn: Mapped[str] = mapped_column(String(128), nullable=True)
    chassis_no: Mapped[str] = mapped_column(String(64), nullable=True)
    price: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    model: Mapped["VehicleModel"] = relationship(
        "VehicleModel", back_populates="variants"
    )

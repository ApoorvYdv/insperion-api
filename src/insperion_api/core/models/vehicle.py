from typing import Optional

from sqlalchemy import JSON, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from insperion_api.core.constants.constants import InspectionStatus
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
    models: Mapped[list["VehicleModel"]] = relationship(
        "VehicleModel", back_populates="brand"
    )


class VehicleModel(VehicleBase):
    __tablename__ = "vehicle_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_brand.id"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(128), nullable=False)
    year_launched: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    body_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    seating_capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    brand: Mapped["VehicleBrand"] = relationship(
        "VehicleBrand", back_populates="models"
    )
    variants: Mapped[list["VehicleVariant"]] = relationship(
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
    price: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    features: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    model: Mapped["VehicleModel"] = relationship(
        "VehicleModel", back_populates="variants"
    )
    units: Mapped[list["VehicleUnit"]] = relationship(
        "VehicleUnit", back_populates="variant"
    )


class VehicleUnit(VehicleBase):
    __tablename__ = "vehicle_unit"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("vehicle_variant.id"), nullable=False
    )

    # Unique identifiers for the physical vehicle
    vin: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    psn: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    chassis_no: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Additional vehicle details
    manufacturing_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Relationships
    variant: Mapped["VehicleVariant"] = relationship(
        "VehicleVariant", back_populates="units"
    )
    inspections: Mapped[list["Inspection"]] = relationship(
        "Inspection", back_populates="unit"
    )


class Inspection(VehicleBase):
    __tablename__ = "inspection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vehicle_unit.id"), nullable=True
    )

    flow_no: Mapped[str] = mapped_column(String(64), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String(128), nullable=False)
    inspection_type_display_name: Mapped[str] = mapped_column(
        String(512), nullable=False
    )

    results: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default=InspectionStatus.PENDING)

    # Relationships
    unit: Mapped[Optional["VehicleUnit"]] = relationship(
        "VehicleUnit", back_populates="inspections"
    )

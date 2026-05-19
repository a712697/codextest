from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base


class ProductCategory(AuditMixin, Base):
    __tablename__ = "product_categories"
    __table_args__ = (UniqueConstraint("name", "parent_id", name="uq_category_name_parent"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id"))


class Brand(AuditMixin, Base):
    __tablename__ = "brands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)


class Supplier(AuditMixin, Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(64))
    phone: Mapped[str | None] = mapped_column(String(32))


class Product(AuditMixin, Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id"))
    brand_id: Mapped[int | None] = mapped_column(ForeignKey("brands.id"))
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    unit: Mapped[str] = mapped_column(String(20), default="件", nullable=False)
    price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    min_stock: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

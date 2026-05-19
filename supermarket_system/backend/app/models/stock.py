from __future__ import annotations

from decimal import Decimal

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import AuditMixin, Base


class Inventory(AuditMixin, Base):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), unique=True, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), default=0, nullable=False)
    locked_quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), default=0, nullable=False)


class StockInOrder(AuditMixin, Base):
    __tablename__ = "stock_in_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"))
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    remark: Mapped[str | None] = mapped_column(Text)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime)
    approved_by: Mapped[int | None] = mapped_column()


class StockInOrderItem(AuditMixin, Base):
    __tablename__ = "stock_in_order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("stock_in_orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=0, nullable=False)


class StockOutOrder(AuditMixin, Base):
    __tablename__ = "stock_out_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    remark: Mapped[str | None] = mapped_column(Text)
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime)
    approved_by: Mapped[int | None] = mapped_column()


class StockOutOrderItem(AuditMixin, Base):
    __tablename__ = "stock_out_order_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("stock_out_orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), nullable=False)


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[int] = mapped_column(nullable=False)
    quantity_delta: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), nullable=False)
    before_quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), nullable=False)
    after_quantity: Mapped[Decimal] = mapped_column(DECIMAL(12, 3), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[DateTime | None] = mapped_column(DateTime)
    created_by: Mapped[int | None] = mapped_column()
    request_id: Mapped[str | None] = mapped_column(String(64))

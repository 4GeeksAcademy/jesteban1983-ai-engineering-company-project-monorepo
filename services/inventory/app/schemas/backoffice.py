# ============================================
# schemas/backoffice.py - Schemas para endpoints de backoffice (/inventory/*)
# ============================================
# Contrato REST del Hito 5 — Interfaz de Gestión de Inventario
# Alineado con vocabulario TrackFlow y campos esperados por el frontend.
# ============================================

from pydantic import BaseModel, Field


class InboundOrderCreate(BaseModel):
    """Schema para registrar una entrada de mercancía."""
    product_id: int
    quantity: int = Field(gt=0, description="Cantidad a ingresar")
    reason: str | None = Field(default=None, description="Motivo de la entrada")


class OutboundOrderCreate(BaseModel):
    """Schema para registrar una salida/venta."""
    product_id: int
    quantity: int = Field(gt=0, description="Cantidad a retirar")
    reason: str | None = Field(default=None, description="Motivo de la salida")
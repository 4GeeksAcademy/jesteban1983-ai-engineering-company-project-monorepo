# ============================================
# routers/backoffice.py - Endpoints para la UI del Backoffice (/inventory/*)
# ============================================
# Proyecto: Hito 5 — Interfaz de Gestión de Inventario (4Geeks Academy)
# 
# REST Contract:
#   GET    /inventory/products           → Lista de productos con current_stock
#   GET    /inventory/products/{id}      → Producto individual con current_stock
#   POST   /inventory/orders/inbound     → Registrar entrada de mercancía
#   POST   /inventory/orders/outbound    → Registrar salida/venta
#   GET    /inventory/orders             → Historial de movimientos
#
# Cada endpoint usa el CRUD existente pero presenta los datos en el formato
# que espera el frontend del backoffice (vocabulario TrackFlow).
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.crud.inventory import inventory
from app.models.inventory import Item
from app.models.movement import Movement
from app.schemas.backoffice import InboundOrderCreate, OutboundOrderCreate

router = APIRouter(
    prefix="/inventory",
    tags=["Backoffice Inventory"],
)


# ============================================
# GET /inventory/products → Lista de productos
# ============================================
@router.get("/products")
async def list_products(
    db: AsyncSession = Depends(get_db),
):
    """Lista todos los productos del inventario con current_stock.
    
    Mapea el campo quantity → current_stock para cumplir con el contrato REST.
    """
    items, total = await inventory.get_items(db=db, skip=0, limit=1000)
    return [
        {
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "current_stock": item.quantity,  # Contrato: current_stock
            "category": item.category,
            "warehouse": item.warehouse,
            "price": float(item.price),
            "min_stock": item.min_stock,
            "is_active": item.is_active,
        }
        for item in items
    ]


# ============================================
# GET /inventory/products/{item_id} → Producto individual
# ============================================
@router.get("/products/{item_id}")
async def get_product(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtiene un producto por ID con current_stock."""
    item = await inventory.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return {
        "id": item.id,
        "name": item.name,
        "sku": item.sku,
        "current_stock": item.quantity,
        "category": item.category,
        "warehouse": item.warehouse,
        "price": float(item.price),
        "min_stock": item.min_stock,
        "is_active": item.is_active,
    }


# ============================================
# POST /inventory/orders/inbound → Registrar entrada
# ============================================
@router.post("/orders/inbound", status_code=status.HTTP_201_CREATED)
async def create_inbound_order(
    body: InboundOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """Registra una entrada de mercancía (inbound).
    
    Usa adjust_stock internamente con quantity_change positivo.
    Crea un movimiento de tipo 'inbound' y actualiza el stock del producto.
    """
    try:
        item = await inventory.adjust_stock(
            db=db,
            item_id=body.product_id,
            quantity_change=body.quantity,  # Positivo → inbound
            reason=body.reason,
        )
    except ValueError as e:
        if "no encontrado" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Obtener el movimiento recién creado para devolverlo en la respuesta
    result = await db.execute(
        select(Movement)
        .where(Movement.item_id == body.product_id)
        .order_by(Movement.created_at.desc())
        .limit(1)
    )
    movement = result.scalar_one()

    return {
        "id": movement.id,
        "product_id": movement.item_id,
        "quantity": movement.quantity,
        "order_type": movement.movement_type,
        "created_at": movement.created_at.isoformat(),
    }


# ============================================
# POST /inventory/orders/outbound → Registrar salida
# ============================================
@router.post("/orders/outbound", status_code=status.HTTP_201_CREATED)
async def create_outbound_order(
    body: OutboundOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """Registra una salida/venta (outbound).
    
    Usa adjust_stock internamente con quantity_change negativo.
    Valida que haya stock suficiente antes de crear el movimiento.
    Si el stock es insuficiente → HTTP 400 con mensaje descriptivo.
    """
    try:
        item = await inventory.adjust_stock(
            db=db,
            item_id=body.product_id,
            quantity_change=-body.quantity,  # Negativo → outbound
            reason=body.reason,
        )
    except ValueError as e:
        if "no encontrado" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        if "Stock insuficiente" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Obtener el movimiento recién creado
    result = await db.execute(
        select(Movement)
        .where(Movement.item_id == body.product_id)
        .order_by(Movement.created_at.desc())
        .limit(1)
    )
    movement = result.scalar_one()

    return {
        "id": movement.id,
        "product_id": movement.item_id,
        "quantity": movement.quantity,
        "order_type": movement.movement_type,
        "created_at": movement.created_at.isoformat(),
    }


# ============================================
# GET /inventory/orders → Historial de movimientos
# ============================================
@router.get("/orders")
async def list_orders(
    db: AsyncSession = Depends(get_db),
):
    """Lista todas las órdenes (movimientos) con información del producto.
    
    JOIN Movements con Items para incluir product_name y user_uuid.
    Ordenado por fecha descendente (más reciente primero).
    """
    query = (
        select(
            Movement.id,
            Movement.item_id,
            Item.name.label("product_name"),
            Movement.movement_type.label("order_type"),
            Movement.quantity,
            Movement.created_at,
            Movement.user_uuid,
        )
        .join(Item, Movement.item_id == Item.id)
        .order_by(Movement.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.mappings().all()

    return [
        {
            "id": row.id,
            "product_id": row.item_id,
            "product_name": row.product_name,
            "quantity": row.quantity,
            "order_type": row.order_type,
            "created_at": row.created_at.isoformat(),
            "user_uuid": row.user_uuid,
        }
        for row in rows
    ]
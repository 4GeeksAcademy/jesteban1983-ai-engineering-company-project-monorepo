# ============================================
# routers/inventory.py - Endpoints de la API de inventario
# ============================================
# Aquí definimos las rutas (URLs) de la API REST.
# Cada función es un endpoint que responde a peticiones HTTP.
#
# FastAPI convierte automáticamente:
# - Los parámetros a JSON
# - Los errores a respuestas HTTP adecuadas
# - Todo a documentación Swagger en /docs

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.inventory import inventory  # Operaciones CRUD
from app.crud.movement import movement as movement_crud  # CRUD de movimientos
from app.dependencies import get_db  # Obtener sesión de BD
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.inventory import ItemCreate, ItemOut, ItemUpdate
from app.schemas.movement import MovementCreate, MovementOut

# ============================================
# Router de inventario
# ============================================
# APIRouter agrupa endpoints relacionados.
# prefix="/api/v1/items" → todas las rutas empiezan con /api/v1/items
# tags=["Inventory"] → se agrupan en Swagger con esta etiqueta
router = APIRouter(
    prefix="/api/v1/items",
    tags=["Inventory"],
)


# ---------------------------------------------------------------
# GET /api/v1/items/ - Listar items (con filtros y paginación)
# ---------------------------------------------------------------
@router.get("/", response_model=PaginatedResponse[ItemOut])
async def list_items(
    pagination: PaginationParams = Depends(),  # Obtiene page y per_page de query params
    category: str | None = Query(None, description="Filtrar por categoría"),
    warehouse: str | None = Query(None, description="Filtrar por almacén"),
    is_active: bool | None = Query(None, description="Filtrar por estado activo"),
    search: str | None = Query(None, description="Buscar por SKU o nombre"),
    low_stock: bool = Query(False, description="Solo items con stock bajo"),
    db: AsyncSession = Depends(get_db),  # Inyecta sesión de BD
):
    """Lista todos los items con filtros opcionales y paginación."""
    skip = (pagination.page - 1) * pagination.per_page  # Calcula offset
    
    items, total = await inventory.get_items(
        db=db,
        skip=skip,
        limit=pagination.per_page,
        category=category,
        warehouse=warehouse,
        is_active=is_active,
        search=search,
        low_stock=low_stock,
    )

    # Calcular total de páginas
    total_pages = (total + pagination.per_page - 1) // pagination.per_page

    return {
        "items": items,
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": total_pages,
    }


# ---------------------------------------------------------------
# GET /api/v1/items/{item_id} - Obtener item por ID
# ---------------------------------------------------------------
@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Obtiene un item específico por su ID."""
    item = await inventory.get_item(db, item_id)
    if item is None:
        # HTTP 404 = Not Found (recurso no existe)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado",
        )
    return item


# ---------------------------------------------------------------
# POST /api/v1/items/ - Crear nuevo item
# ---------------------------------------------------------------
@router.post(
    "/",
    response_model=ItemOut,
    status_code=status.HTTP_201_CREATED,  # 201 = Created
)
async def create_item(
    data: ItemCreate,  # FastAPI valida el body automáticamente con ItemCreate
    db: AsyncSession = Depends(get_db),
):
    """Crea un nuevo item de inventario."""
    try:
        item = await inventory.create_item(db, data)
        return item
    except ValueError as e:
        # HTTP 409 = Conflict (recurso duplicado, ej: SKU repetido)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


# ---------------------------------------------------------------
# PUT /api/v1/items/{item_id} - Actualizar item
# ---------------------------------------------------------------
@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: int,
    data: ItemUpdate,  # Solo los campos enviados se actualizan
    db: AsyncSession = Depends(get_db),
):
    """Actualiza un item existente (actualización parcial)."""
    item = await inventory.update_item(db, item_id, data)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado",
        )
    return item


# ---------------------------------------------------------------
# DELETE /api/v1/items/{item_id} - Eliminar (desactivar) item
# ---------------------------------------------------------------
@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Elimina (desactiva) un item.
    
    NOTA: No borra físicamente, solo marca is_active=False.
    Esto es "borrado lógico" (soft delete).
    """
    deleted = await inventory.delete_item(db, item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado",
        )
    return {"message": f"Item {item_id} desactivado correctamente"}


# ---------------------------------------------------------------
# POST /api/v1/items/{item_id}/adjust-stock - Ajustar stock
# ---------------------------------------------------------------
@router.post("/{item_id}/adjust-stock", response_model=ItemOut)
async def adjust_stock(
    item_id: int,
    data: MovementCreate,  # Tipo de movimiento y cantidad
    db: AsyncSession = Depends(get_db),
):
    """
    Ajusta el stock de un item y registra un movimiento.
    
    Para INCREMENTAR stock: movement_type="inbound", quantity=10
    Para DECREMENTAR stock: movement_type="outbound", quantity=5
    """
    # Convertir tipo de movimiento a cambio de cantidad (+/-)
    if data.movement_type == "outbound":
        quantity_change = -data.quantity  # Negativo = disminuye stock
    else:
        quantity_change = data.quantity   # Positivo = aumenta stock

    try:
        item = await inventory.adjust_stock(
            db, item_id, quantity_change, data.reason
        )
        return item
    except ValueError as e:
        # Puede ser: item no encontrado o stock insuficiente
        if "no encontrado" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,  # 400 = Bad Request
            detail=str(e),
        )


# ---------------------------------------------------------------
# GET /api/v1/items/{item_id}/movements - Historial de movimientos
# ---------------------------------------------------------------
@router.get("/{item_id}/movements", response_model=PaginatedResponse[MovementOut])
async def list_movements(
    item_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el historial de movimientos de un item."""
    # Primero verificar que el item existe
    item = await inventory.get_item(db, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item con ID {item_id} no encontrado",
        )

    skip = (pagination.page - 1) * pagination.per_page
    movements, total = await movement_crud.get_movements(
        db, item_id, skip=skip, limit=pagination.per_page
    )

    total_pages = (total + pagination.per_page - 1) // pagination.per_page

    return {
        "items": movements,
        "total": total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_pages": total_pages,
    }
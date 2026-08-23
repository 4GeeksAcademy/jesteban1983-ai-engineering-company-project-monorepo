# ============================================
# crud/movement.py - Operaciones CRUD para Movimientos
# ============================================

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.movement import Movement


class MovementCRUD:
    """
    Clase para operaciones de movimientos de inventario.
    Recupera el historial de cambios de stock de un item.
    """

    async def get_movements(
        self,
        db: AsyncSession,
        item_id: int,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Movement], int]:
        """
        Obtiene el historial de movimientos de un item.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            skip: Registros a saltar (paginación)
            limit: Máximo de registros
        
        Returns:
            tuple[list[Movement], int]: (movimientos, total)
        """
        # SELECT * FROM inventory_movements WHERE item_id = ? ORDER BY created_at DESC
        query = (
            select(Movement)
            .where(Movement.item_id == item_id)
            .order_by(Movement.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # También necesitamos el total
        count_query = select(Movement.id).where(Movement.item_id == item_id)
        total_result = await db.execute(count_query)
        total = len(total_result.scalars().all())

        result = await db.execute(query)
        movements = result.scalars().all()

        return list(movements), total


# Instancia única
movement = MovementCRUD()
# ============================================
# crud/inventory.py - Operaciones CRUD para Items
# ============================================
# CRUD = Create, Read, Update, Delete
# Aquí están todas las funciones que interactúan con la base de datos
# para gestionar items de inventario.
#
# Cada función es ASÍNCRONA (async) = no bloquea el servidor
# mientras espera a la base de datos.

from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func  # select() para consultas SQL
from sqlalchemy.ext.asyncio import AsyncSession  # Sesión asíncrona
from sqlalchemy.orm import selectinload  # Para cargar relaciones

from app.models.inventory import Item
from app.models.movement import Movement
from app.schemas.inventory import ItemCreate, ItemUpdate
from app.schemas.movement import MovementCreate


class InventoryCRUD:
    """
    Clase que agrupa todas las operaciones CRUD de inventario.
    
    En lugar de funciones sueltas, usamos una clase para organizar mejor.
    Cada método recibe la sesión de BD como primer parámetro.
    """

    async def get_items(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        warehouse: Optional[str] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        low_stock: bool = False,
    ) -> tuple[list[Item], int]:
        """
        Lista items con filtros opcionales y paginación.
        
        Args:
            db: Sesión de base de datos
            skip: Registros a saltar (para paginación)
            limit: Máximo de registros a devolver
            category: Filtrar por categoría
            warehouse: Filtrar por almacén
            is_active: Filtrar por estado activo/inactivo
            search: Búsqueda por texto en SKU o nombre
            low_stock: Solo items con stock bajo (quantity < min_stock)
        
        Returns:
            tuple[list[Item], int]: (lista de items, total de items)
        """
        # Construimos la consulta base: SELECT * FROM inventory_items
        query = select(Item)

        # --- Filtros condicionales ---
        # Solo añadimos filtro si el parámetro fue proporcionado
        if category is not None:
            query = query.where(Item.category == category)
        
        if warehouse is not None:
            query = query.where(Item.warehouse == warehouse)
        
        if is_active is not None:
            query = query.where(Item.is_active == is_active)
        
        if search is not None:
            # ILIKE = búsqueda sin distinción mayúsculas/minúsculas
            # Buscamos tanto en SKU como en nombre
            query = query.where(
                Item.sku.ilike(f"%{search}%") | Item.name.ilike(f"%{search}%")
            )
        
        if low_stock:
            # Stock bajo = quantity < min_stock
            query = query.where(Item.quantity < Item.min_stock)

        # --- Obtener total (sin paginación) ---
        # Necesitamos el total para la respuesta paginada
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # --- Aplicar paginación ---
        # Ordenamos por ID y aplicamos skip/limit
        query = query.order_by(Item.id).offset(skip).limit(limit)

        # --- Ejecutar consulta ---
        result = await db.execute(query)
        items = result.scalars().all()
        # scalars() obtiene los objetos Item directamente

        return list(items), total

    async def get_item(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> Optional[Item]:
        """
        Obtiene un item por su ID.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item a buscar
        
        Returns:
            Optional[Item]: El item si existe, None si no
        """
        # SELECT * FROM inventory_items WHERE id = item_id
        result = await db.execute(select(Item).where(Item.id == item_id))
        # scalar_one_or_none() devuelve el item o None si no existe
        return result.scalar_one_or_none()

    async def get_item_by_sku(
        self,
        db: AsyncSession,
        sku: str,
    ) -> Optional[Item]:
        """
        Obtiene un item por su SKU (código único).
        
        Args:
            db: Sesión de base de datos
            sku: SKU del item a buscar
        
        Returns:
            Optional[Item]: El item si existe, None si no
        """
        result = await db.execute(select(Item).where(Item.sku == sku))
        return result.scalar_one_or_none()

    async def create_item(
        self,
        db: AsyncSession,
        data: ItemCreate,
    ) -> Item:
        """
        Crea un nuevo item de inventario.
        
        Primero verifica que el SKU no esté duplicado.
        Si el SKU ya existe, lanza una excepción.
        
        Args:
            db: Sesión de base de datos
            data: Datos validados del nuevo item
        
        Returns:
            Item: El item creado (con id asignado)
        
        Raises:
            ValueError: Si el SKU ya existe
        """
        # 1. Verificar que el SKU no exista ya
        existing = await self.get_item_by_sku(db, data.sku)
        if existing is not None:
            raise ValueError(f"Ya existe un item con SKU '{data.sku}'")

        # 2. Crear el objeto Item con los datos del schema
        item = Item(
            sku=data.sku,
            name=data.name,
            description=data.description,
            quantity=data.quantity,
            price=data.price,
            category=data.category,
            warehouse=data.warehouse,
            min_stock=data.min_stock,
            is_active=data.is_active,
        )

        # 3. Añadir a la sesión (pendiente de guardar)
        db.add(item)

        # 4. Guardar en la base de datos
        await db.commit()

        # 5. Refrescar el objeto (obtener id y valores de la BD)
        await db.refresh(item)

        return item

    async def update_item(
        self,
        db: AsyncSession,
        item_id: int,
        data: ItemUpdate,
    ) -> Optional[Item]:
        """
        Actualiza un item existente (solo los campos proporcionados).
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item a actualizar
            data: Datos a actualizar (solo los campos con valor)
        
        Returns:
            Optional[Item]: Item actualizado o None si no existe
        """
        # 1. Buscar el item
        item = await self.get_item(db, item_id)
        if item is None:
            return None

        # 2. Validar SKU único si se está actualizando el SKU
        update_data = data.model_dump(exclude_unset=True)
        if "sku" in update_data and update_data["sku"] != item.sku:
            existing = await self.get_item_by_sku(db, update_data["sku"])
            if existing is not None:
                raise ValueError(f"Ya existe un item con SKU '{update_data['sku']}'")

        # 3. Actualizar solo los campos que vienen en data
        # model_dump(exclude_unset=True) devuelve solo los campos que el usuario envió
        for field, value in update_data.items():
            # setattr(obj, "name", value) = obj.name = value
            setattr(item, field, value)

        # 4. Guardar cambios
        await db.commit()
        await db.refresh(item)

        return item

    async def delete_item(
        self,
        db: AsyncSession,
        item_id: int,
    ) -> bool:
        """
        Elimina un item (borrado lógico: is_active = False).
        
        No borramos físicamente el registro, solo lo desactivamos.
        Esto permite recuperar datos históricos.
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item a desactivar
        
        Returns:
            bool: True si se desactivó, False si no existía
        """
        item = await self.get_item(db, item_id)
        if item is None:
            return False

        # Borrado lógico: marcamos como inactivo
        item.is_active = False
        
        await db.commit()
        return True

    async def adjust_stock(
        self,
        db: AsyncSession,
        item_id: int,
        quantity_change: int,
        reason: Optional[str] = None,
    ) -> Item:
        """
        Ajusta el stock de un item y registra un movimiento.
        
        quantity_change puede ser:
        - Positivo (+5) = aumenta stock (entrada)
        - Negativo (-3) = disminuye stock (salida)
        
        Args:
            db: Sesión de base de datos
            item_id: ID del item
            quantity_change: Cambio de cantidad (+/-)
            reason: Razón del ajuste
        
        Returns:
            Item: Item con stock actualizado
        
        Raises:
            ValueError: Si item no existe o stock insuficiente
        """
        # 1. Buscar el item
        item = await self.get_item(db, item_id)
        if item is None:
            raise ValueError(f"Item con ID {item_id} no encontrado")

        # 2. Validar que haya stock suficiente si es salida
        if quantity_change < 0 and item.quantity + quantity_change < 0:
            raise ValueError(
                f"Stock insuficiente. Actual: {item.quantity}, "
                f"requerido: {abs(quantity_change)}"
            )

        # 3. Actualizar stock (quantity_change puede ser negativo)
        item.quantity += quantity_change
        item.quantity = max(0, item.quantity)  # Nunca menor que 0

        # 4. Determinar tipo de movimiento según el cambio
        if quantity_change > 0:
            movement_type = "inbound"
            movement_qty = quantity_change
        elif quantity_change < 0:
            movement_type = "outbound"
            movement_qty = abs(quantity_change)
        else:
            movement_type = "adjustment"
            movement_qty = 0

        # 5. Registrar el movimiento en la tabla de auditoría
        movement = Movement(
            item_id=item_id,
            movement_type=movement_type,
            quantity=movement_qty,
            reason=reason,
        )
        db.add(movement)

        # 6. Guardar todo
        await db.commit()
        await db.refresh(item)

        return item


# ---- Instancia única ----
# Creamos una instancia de InventoryCRUD que se reutiliza en toda la app
inventory = InventoryCRUD()
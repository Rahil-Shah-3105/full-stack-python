import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
import time
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    logger.error(">>> Entering read_items(session=%s,current_user=%s,skip=%s,limit=%s)", session, current_user, skip, limit, extra={"event.action": "read_items", "logrite.current_user": current_user, "logrite.skip": skip, "logrite.limit": limit})
    """
    Retrieve items.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        logger.error("read_items(session=%s,current_user=%s,skip=%s,limit=%s): count → %s", session, current_user, skip, limit, count, extra={"event.action": "read_items", "logrite.current_user": current_user, "logrite.skip": skip, "logrite.limit": limit})
        statement = (
            select(Item).order_by(col(Item.created_at).desc()).offset(skip).limit(limit)
        )
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == current_user.id)
            .order_by(col(Item.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    items_public = [ItemPublic.model_validate(item) for item in items]
    logger.error("read_items(session=%s,current_user=%s,skip=%s,limit=%s): items_public → %s", session, current_user, skip, limit, items_public, extra={"event.action": "read_items", "logrite.current_user": current_user, "logrite.skip": skip, "logrite.limit": limit})
    logger.warning("<<< Exiting read_items(session=%s,current_user=%s,skip=%s,limit=%s)", session, current_user, skip, limit, extra={"event.action": "read_items", "logrite.current_user": current_user, "logrite.skip": skip, "logrite.limit": limit})
    return ItemsPublic(data=items_public, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    __log_start = time.time()
    """
    Get item by ID.
    """
    logger.error(">>> Entering read_item(session=%s,current_user=%s,id=%s)", session, current_user, id, extra={"event.action": "read_item", "logrite.current_user": current_user, "logrite.id": id})
    item = session.get(Item, id)
    logger.error("read_item(session,current_user,id)=%s,%s,%s: find operation took %s ms", session, current_user, id, int((time.time() - __log_start) * 1000), extra={"event.action": "read_item", "event.category": "database", "logrite.current_user": current_user, "logrite.id": id})
    logger.error("read_item(session=%s,current_user=%s,id=%s): item → %s", session, current_user, id, item, extra={"event.action": "read_item", "logrite.current_user": current_user, "logrite.id": id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    logger.warning("<<< Exiting read_item(session=%s,current_user=%s,id=%s)", session, current_user, id, extra={"event.action": "read_item", "logrite.current_user": current_user, "logrite.id": id})
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item = Item.model_validate(item_in, update={"owner_id": current_user.id})
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    logger.error(">>> Entering update_item(session=%s,current_user=%s,id=%s,item_in=%s)", session, current_user, id, item_in, extra={"event.action": "update_item", "logrite.current_user": current_user, "logrite.id": id, "logrite.item_in": item_in})
    """
    Update an item.
    """
    item = session.get(Item, id)
    logger.error("update_item(session=%s,current_user=%s,id=%s,item_in=%s): item → %s", session, current_user, id, item_in, item, extra={"event.action": "update_item", "logrite.current_user": current_user, "logrite.id": id, "logrite.item_in": item_in})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    logger.error("update_item(session=%s,current_user=%s,id=%s,item_in=%s): update_dict → %s", session, current_user, id, item_in, update_dict, extra={"event.action": "update_item", "logrite.current_user": current_user, "logrite.id": id, "logrite.item_in": item_in})
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    logger.warning("<<< Exiting update_item(session=%s,current_user=%s,id=%s,item_in=%s)", session, current_user, id, item_in, extra={"event.action": "update_item", "logrite.current_user": current_user, "logrite.id": id, "logrite.item_in": item_in})
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    logger.error(">>> Entering delete_item(session=%s,current_user=%s,id=%s)", session, current_user, id, extra={"event.action": "delete_item", "logrite.current_user": current_user, "logrite.id": id})
    """
    Delete an item.
    """
    item = session.get(Item, id)
    logger.error("delete_item(session=%s,current_user=%s,id=%s): item → %s", session, current_user, id, item, extra={"event.action": "delete_item", "logrite.current_user": current_user, "logrite.id": id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    logger.warning("<<< Exiting delete_item(session=%s,current_user=%s,id=%s)", session, current_user, id, extra={"event.action": "delete_item", "logrite.current_user": current_user, "logrite.id": id})
    return Message(message="Item deleted successfully")

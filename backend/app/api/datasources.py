import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.datasource import Datasource
from app.schemas.datasource import (
    DatasourceCreate, DatasourceUpdate, DatasourceResponse,
    TableInfo, ColumnInfo,
)
from app.services.datasource_service import (
    build_connection_url, test_connection, get_tables, get_columns,
)

router = APIRouter()


@router.post("", response_model=DatasourceResponse)
def create_datasource(data: DatasourceCreate, db: Session = Depends(get_db)):
    ds = Datasource(**data.model_dump())
    db.add(ds)
    db.commit()
    db.refresh(ds)
    return ds


@router.get("", response_model=list[DatasourceResponse])
def list_datasources(db: Session = Depends(get_db)):
    return db.query(Datasource).all()


@router.get("/{ds_id}", response_model=DatasourceResponse)
def get_datasource(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    return ds


@router.put("/{ds_id}", response_model=DatasourceResponse)
def update_datasource(
    ds_id: uuid.UUID, data: DatasourceUpdate, db: Session = Depends(get_db)
):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(ds, key, val)
    db.commit()
    db.refresh(ds)
    return ds


@router.delete("/{ds_id}")
def delete_datasource(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    db.delete(ds)
    db.commit()
    return {"message": "已删除"}


@router.post("/{ds_id}/test")
def test_ds_connection(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    url = build_connection_url(
        ds.db_type, ds.host, ds.port, ds.database, ds.username, ds.password
    )
    return test_connection(url)


@router.get("/{ds_id}/tables", response_model=list[TableInfo])
def list_tables(ds_id: uuid.UUID, db: Session = Depends(get_db)):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    url = build_connection_url(
        ds.db_type, ds.host, ds.port, ds.database, ds.username, ds.password
    )
    tables = get_tables(url)
    return [{"table_name": t} for t in tables]


@router.get("/{ds_id}/tables/{table}/columns", response_model=list[ColumnInfo])
def list_columns(
    ds_id: uuid.UUID, table: str, db: Session = Depends(get_db)
):
    ds = db.query(Datasource).filter(Datasource.id == ds_id).first()
    if not ds:
        raise HTTPException(404, "数据源不存在")
    url = build_connection_url(
        ds.db_type, ds.host, ds.port, ds.database, ds.username, ds.password
    )
    return get_columns(url, table)

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError


def build_connection_url(db_type: str, host: str, port: int,
                         database: str, username: str, password: str) -> str:
    if db_type == "mysql":
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "postgresql":
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    elif db_type == "sqlserver":
        return (
            f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}"
            "?driver=ODBC+Driver+17+for+SQL+Server"
        )
    raise ValueError(f"Unsupported db_type: {db_type}")


def test_connection(url: str) -> dict:
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"success": True, "message": "连接成功"}
    except OperationalError as e:
        return {"success": False, "message": str(e)}


def get_tables(url: str) -> list[str]:
    engine = create_engine(url)
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_columns(url: str, table_name: str) -> list[dict]:
    engine = create_engine(url)
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [
        {
            "column_name": col["name"],
            "data_type": str(col["type"]),
            "is_nullable": col.get("nullable", True),
        }
        for col in columns
    ]

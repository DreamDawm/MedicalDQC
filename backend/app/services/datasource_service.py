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

    # 从 URL 中提取数据库名和数据库类型
    # URL 格式: mysql+pymysql://user:pass@host:port/database
    db_type = "mysql" if "mysql" in url else "postgresql" if "postgresql" in url else "sqlserver"
    database = url.split("/")[-1].split("?")[0]

    # 验证数据库提取是否成功
    if not database:
        raise ValueError("无法从连接 URL 提取数据库名")

    # 获取基础列信息
    columns = inspector.get_columns(table_name)

    # 对于 MySQL，查询 INFORMATION_SCHEMA 获取列注释
    comment_map = {}
    if db_type == "mysql":
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT COLUMN_NAME, COLUMN_COMMENT
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME = :table
                """),
                {"schema": database, "table": table_name}
            )
            for row in result:
                comment_map[row[0]] = row[1] or ""

    return [
        {
            "column_name": col["name"],
            # 只保留类型名称，移除 collate 等额外信息
            "data_type": str(col["type"]).split("(")[0].upper(),
            "is_nullable": col.get("nullable", True),
            "comment": comment_map.get(col["name"], ""),
        }
        for col in columns
    ]

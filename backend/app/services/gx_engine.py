import sqlalchemy
from sqlalchemy import create_engine, text

from app.services.datasource_service import build_connection_url


def run_expectations(
    db_type: str,
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
    table_name: str,
    expectations: list[dict],
) -> dict:
    connection_url = build_connection_url(
        db_type, host, port, database, username, password
    )

    # 对于 MySQL，expect_column_values_to_be_unique 有 SQL 语法兼容问题
    # 需要用原生 SQL 处理
    unique_expectations = [
        exp for exp in expectations
        if exp["expectation_type"] == "expect_column_values_to_be_unique"
    ]
    other_expectations = [
        exp for exp in expectations
        if exp["expectation_type"] != "expect_column_values_to_be_unique"
    ]

    results = []

    # 处理唯一性检查（使用原生 SQL）
    if unique_expectations:
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            for exp in unique_expectations:
                column = exp["kwargs"].get("column")
                display_name = exp.get("display_name")
                mostly = exp.get("kwargs", {}).get("mostly")

                # 检查重复值
                sql = text(f"""
                    SELECT COUNT(*) as total,
                           COUNT(DISTINCT {column}) as unique_count,
                           COUNT({column}) as non_null_count
                    FROM {table_name}
                """)
                result = conn.execute(sql).fetchone()
                total = result[0]
                unique_count = result[1]
                non_null_count = result[2]

                # 判断是否唯一
                null_count = total - non_null_count
                duplicate_count = non_null_count - unique_count

                if mostly is not None:
                    # 使用 mostly 参数，允许部分失败
                    success_rate = unique_count / non_null_count if non_null_count > 0 else 1.0
                    success = success_rate >= mostly
                else:
                    # 严格要求所有值唯一
                    success = (unique_count == non_null_count) and (duplicate_count == 0)

                results.append({
                    "expectation_type": "expect_column_values_to_be_unique",
                    "display_name": display_name,
                    "success": success,
                    "kwargs": exp["kwargs"],
                    "result": {
                        "total": total,
                        "unique_count": unique_count,
                        "non_null_count": non_null_count,
                        "duplicate_count": duplicate_count,
                    },
                })

    # 处理其他 expectations（使用 GX）
    if other_expectations:
        import great_expectations as gx
        from great_expectations.core import ExpectationSuite

        context = gx.get_context()

        datasource = context.data_sources.add_sql(
            name="runtime_ds",
            connection_string=connection_url,
        )

        asset = datasource.add_table_asset(
            name="runtime_asset",
            table_name=table_name,
        )

        batch_definition = asset.add_batch_definition_whole_table(
            name="runtime_batch"
        )

        suite = ExpectationSuite(name="runtime_suite")

        # 建立 expectation_type 到 display_name 的映射
        display_name_map = {}

        for exp in other_expectations:
            exp_type = exp["expectation_type"]
            kwargs = exp.get("kwargs", {})
            if "display_name" in exp:
                display_name_map[exp_type] = exp["display_name"]
            suite.add_expectation(
                gx.expectations.registry.get_expectation_impl(exp_type)(**kwargs)
            )

        batch = batch_definition.get_batch()
        validation_result = batch.validate(suite)

        for r in validation_result.results:
            exp_type = r.expectation_config.type
            results.append({
                "expectation_type": exp_type,
                "display_name": display_name_map.get(exp_type),
                "success": r.success,
                "kwargs": r.expectation_config.kwargs,
                "result": r.result if hasattr(r, "result") else {},
            })

    return {
        "success": all(r["success"] for r in results),
        "results": results,
        "statistics": {
            "evaluated": len(results),
            "passed": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
        },
    }

import sqlalchemy
from sqlalchemy import create_engine, text, inspect

from app.services.datasource_service import build_connection_url


def get_primary_key_columns(engine, table_name: str) -> list[str]:
    """获取表的主键列名列表"""
    try:
        inspector = inspect(engine)
        pk = inspector.get_pk_constraint(table_name)
        return pk.get("constrained_columns", [])
    except Exception:
        return []


def get_failed_records_sample(
    engine,
    table_name: str,
    column: str,
    primary_keys: list[str],
    limit: int = 10,
) -> list[dict]:
    """获取失败记录的样本（前10条），包含主键ID和失败值"""
    try:
        if not primary_keys:
            # 没有主键时，只获取失败值
            sql = text(f"""
                SELECT DISTINCT `{column}` as failed_value
                FROM `{table_name}`
                WHERE `{column}` IS NOT NULL
                LIMIT :limit
            """)
            with engine.connect() as conn:
                result = conn.execute(sql, {"limit": limit})
                return [{"failed_value": row[0]} for row in result.fetchall()]
        else:
            # 有主键时，获取主键ID和失败值
            pk_select = ", ".join([f"`{pk}`" for pk in primary_keys])
            sql = text(f"""
                SELECT {pk_select}, `{column}` as failed_value
                FROM `{table_name}`
                WHERE `{column}` IS NOT NULL
                LIMIT :limit
            """)
            with engine.connect() as conn:
                result = conn.execute(sql, {"limit": limit})
                records = []
                for row in result.fetchall():
                    record = {
                        "primary_key": {pk: str(getattr(row, pk, row[i]))
                                       for i, pk in enumerate(primary_keys)},
                        "failed_value": row.failed_value,
                    }
                    records.append(record)
                return records
    except Exception as e:
        return [{"error": str(e)}]


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

    engine = create_engine(connection_url)

    # 获取表的主键列
    primary_keys = get_primary_key_columns(engine, table_name)

    # 对于 MySQL，expect_column_values_to_be_unique 有 SQL 语法兼容问题
    # 需要用原生 SQL 处理
    unique_expectations = [
        exp for exp in expectations
        if exp["expectation_type"] == "expect_column_values_to_be_unique"
    ]
    pair_gte_expectations = [
        exp for exp in expectations
        if exp["expectation_type"] == "expect_column_pair_values_A_to_be_greater_than_or_equal_to_B"
    ]
    other_expectations = [
        exp for exp in expectations
        if exp["expectation_type"] not in (
            "expect_column_values_to_be_unique",
            "expect_column_pair_values_A_to_be_greater_than_or_equal_to_B",
        )
    ]

    results = []

    # 处理唯一性检查（使用原生 SQL）
    if unique_expectations:
        with engine.connect() as conn:
            for exp in unique_expectations:
                column = exp["kwargs"].get("column")
                display_name = exp.get("display_name")
                rule_id = exp.get("rule_id")
                mostly = exp.get("kwargs", {}).get("mostly")

                # 检查重复值
                sql = text(f"""
                    SELECT COUNT(*) as total,
                           COUNT(DISTINCT `{column}`) as unique_count,
                           COUNT(`{column}`) as non_null_count
                    FROM `{table_name}`
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

                # 获取重复值样本（失败的枚举值）
                failed_sample = []
                if not success and duplicate_count > 0:
                    failed_sample_sql = text(f"""
                        SELECT `{column}` as value, COUNT(*) as count
                        FROM `{table_name}`
                        WHERE `{column}` IS NOT NULL
                        GROUP BY `{column}`
                        HAVING COUNT(*) > 1
                        ORDER BY COUNT(*) DESC
                        LIMIT 10
                    """)
                    dup_result = conn.execute(failed_sample_sql)
                    failed_sample = [
                        {"value": row[0], "count": row[1]}
                        for row in dup_result.fetchall()
                    ]

                results.append({
                    "expectation_type": "expect_column_values_to_be_unique",
                    "display_name": display_name,
                    "rule_id": rule_id,
                    "success": success,
                    "kwargs": exp["kwargs"],
                    "table_name": table_name,
                    "column_name": column,
                    "result": {
                        "element_count": total,
                        "null_count": null_count,
                        "unique_count": unique_count,
                        "non_null_count": non_null_count,
                        "unexpected_count": duplicate_count,
                        "unexpected_percent": round(duplicate_count / non_null_count * 100, 2) if non_null_count > 0 else 0,
                        "partial_unexpected_counts": failed_sample,
                    },
                })

    # 处理 A >= B 跨列比较（GX Core 不支持，使用原生 SQL）
    if pair_gte_expectations:
        with engine.connect() as conn:
            for exp in pair_gte_expectations:
                kwargs = exp.get("kwargs", {})
                column_a = kwargs.get("column_A")
                column_b = kwargs.get("column_B")
                display_name = exp.get("display_name")
                rule_id = exp.get("rule_id")
                mostly = kwargs.get("mostly")

                sql = text(f"""
                    SELECT
                        COUNT(*) as total,
                        SUM(CASE WHEN `{column_a}` IS NOT NULL AND `{column_b}` IS NOT NULL
                                  AND `{column_a}` >= `{column_b}` THEN 1 ELSE 0 END) as passed,
                        SUM(CASE WHEN `{column_a}` IS NOT NULL AND `{column_b}` IS NOT NULL
                                  AND `{column_a}` < `{column_b}` THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN `{column_a}` IS NULL OR `{column_b}` IS NULL THEN 1 ELSE 0 END) as null_count
                    FROM `{table_name}`
                """)
                row = conn.execute(sql).fetchone()
                total = int(row[0])
                passed_count = int(row[1])
                failed_count = int(row[2])
                null_count = int(row[3])
                non_null_count = total - null_count

                if mostly is not None:
                    success = (passed_count / non_null_count >= mostly) if non_null_count > 0 else True
                else:
                    success = failed_count == 0

                results.append({
                    "expectation_type": "expect_column_pair_values_A_to_be_greater_than_or_equal_to_B",
                    "display_name": display_name,
                    "rule_id": rule_id,
                    "success": success,
                    "kwargs": kwargs,
                    "table_name": table_name,
                    "column_name": f"{column_a} >= {column_b}",
                    "result": {
                        "element_count": total,
                        "null_count": null_count,
                        "unexpected_count": failed_count,
                        "unexpected_percent": round(float(failed_count) / non_null_count * 100, 2) if non_null_count > 0 else 0,
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

        # 建立 expectation_type 到 rule_id 和 display_name 的映射
        exp_info_map = {}

        for exp in other_expectations:
            exp_type = exp["expectation_type"]
            kwargs = exp.get("kwargs", {})
            exp_info_map[exp_type] = {
                "display_name": exp.get("display_name"),
                "rule_id": exp.get("rule_id"),
            }
            suite.add_expectation(
                gx.expectations.registry.get_expectation_impl(exp_type)(**kwargs)
            )

        batch = batch_definition.get_batch()
        validation_result = batch.validate(suite)

        for r in validation_result.results:
            exp_type = r.expectation_config.type
            exp_info = exp_info_map.get(exp_type, {})
            kwargs = r.expectation_config.kwargs
            column = kwargs.get("column")

            # 提取 GX 返回的详细结果
            result_data = r.result if hasattr(r, "result") else {}

            # 标准化结果数据结构
            result_dict = {
                "element_count": result_data.get("element_count", 0),
                "unexpected_count": result_data.get("unexpected_count", 0),
                "unexpected_percent": result_data.get("unexpected_percent", 0),
                "partial_unexpected_counts": result_data.get("partial_unexpected_counts", []),
                "partial_unexpected_list": result_data.get("partial_unexpected_list", []),
            }

            # 如果有失败记录，获取更详细的失败样本（包含主键ID）
            failed_sample = []
            if not r.success and column:
                # 从 partial_unexpected_list 获取失败值样本
                unexpected_values = result_dict.get("partial_unexpected_list", [])[:10]
                if unexpected_values:
                    failed_sample = [
                        {"value": v} for v in unexpected_values
                    ]

            results.append({
                "expectation_type": exp_type,
                "display_name": exp_info.get("display_name"),
                "rule_id": exp_info.get("rule_id"),
                "success": r.success,
                "kwargs": kwargs,
                "table_name": table_name,
                "column_name": column or "全表",
                "result": result_dict,
                "failed_sample": failed_sample,
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

import great_expectations as gx
from great_expectations.core import ExpectationSuite

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

    for exp in expectations:
        exp_type = exp["expectation_type"]
        kwargs = exp.get("kwargs", {})
        suite.add_expectation(
            gx.expectations.registry.get_expectation_impl(exp_type)(**kwargs)
        )

    batch = batch_definition.get_batch()

    validation_result = batch.validate(suite)

    results = []
    for r in validation_result.results:
        results.append({
            "expectation_type": r.expectation_config.type,
            "success": r.success,
            "kwargs": r.expectation_config.kwargs,
            "result": r.result if hasattr(r, "result") else {},
        })

    return {
        "success": validation_result.success,
        "results": results,
        "statistics": {
            "evaluated": len(results),
            "passed": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
        },
    }

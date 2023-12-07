import azure.functions as func
import logging
import json
import traceback

bp_compare_tables = func.Blueprint()


def replace_null_with_empty_string(row):
    # Replace null values with empty strings in the given row
    return {key: value if value is not None else "" for key, value in row.items()}


def compare_rows(row1, row2):
    # Compare each key-value pair in the rows
    for key, value in row1.items():
        if key != "contest_id" and row2.get(key) != value:
            return False
    return True


def compare_tables(sql_table, dataverse_table):
    # Replace null values with empty strings in both tables
    sql_table = [replace_null_with_empty_string(row) for row in sql_table]
    dataverse_table = [replace_null_with_empty_string(row) for row in dataverse_table]

    # Extract contest_ids from each table
    ids_sql_table = set(row["contest_id"] for row in sql_table)
    ids_dataverse_table = set(row["contest_id"] for row in dataverse_table)

    # Rows only in sql_table
    only_in_sql_table = [
        row for row in sql_table if row["contest_id"] not in ids_dataverse_table
    ]

    # Rows only in dataverse_table
    only_in_dataverse_table = [
        row for row in dataverse_table if row["contest_id"] not in ids_sql_table
    ]

    # Rows in both tables but with different values
    # common_rows_diff_values = [
    #     row
    #     for row in sql_table
    #     if row in dataverse_table
    #     and row
    #     != next(
    #         (r for r in dataverse_table if r["contest_id"] == row["contest_id"]), None
    #     )
    # ]

    common_rows_diff_values = [
        row1
        for row1 in sql_table
        for row2 in dataverse_table
        if row1["contest_id"] == row2["contest_id"] and not compare_rows(row1, row2)
    ]

    # Rows in both tables that are the same
    # common_rows_same_values = [
    #     row
    #     for row in sql_table
    #     if row in dataverse_table
    #     and row
    #     == next(
    #         (r for r in dataverse_table if r["contest_id"] == row["contest_id"]), None
    #     )
    # ]
    common_rows_same_values = [
        row1
        for row1 in sql_table
        for row2 in dataverse_table
        if row1["contest_id"] == row2["contest_id"] and compare_rows(row1, row2)
    ]

    return (
        only_in_sql_table,
        only_in_dataverse_table,
        common_rows_same_values,
        common_rows_diff_values,
    )


@bp_compare_tables.route(route="comparetbl")
def comparetbl(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        sql_table = req_body.get("sql_table", [])
        dataverse_table = req_body.get("dataverse_table", [])

        (
            only_in_sql_table,
            only_in_dataverse_table,
            common_rows_same_values,
            common_rows_diff_values,
        ) = compare_tables(sql_table, dataverse_table)

        result = {
            "only_in_sql_table": only_in_sql_table,
            "only_in_dataverse_table": only_in_dataverse_table,
            "common_rows_same_values": common_rows_same_values,
            "common_rows_diff_values": common_rows_diff_values,
        }

        return func.HttpResponse(
            json.dumps(result), mimetype="application/json", status_code=200
        )

    except Exception as e:
        # Capture the line number where the exception occurred
        tb = traceback.extract_tb(e.__traceback__)
        line_number = tb[-1][1]
        error_message = {
            "error": str(e),
            "line_number": line_number,
            "stack_trace": traceback.format_exc(),
        }
        return func.HttpResponse(
            json.dumps(error_message), status_code=400, mimetype="application/json"
        )

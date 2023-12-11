import azure.functions as func
import logging
import json
import traceback

bp_compare_tables = func.Blueprint()


def replace_null_with_empty_string(row):
    # Replace null values with empty strings in the given row
    return {key: value if value is not None else "" for key, value in row.items()}


def compare_rows(row1, row2, primary_key):
    # Compare each key-value pair in the rows (excluding the primary key)
    # This ignores any additional columns in row2 because it only iterate through
    # fields in row1. It allows us to attached GUIDs columns in the dataverse tables
    # for use with updates and deletes/deactivate and not affecting the comparison
    # results.
    for key, value in row1.items():
        if key != primary_key and row2.get(key) != value:
            return False
    return True


def copy_dv_guid(row1, row2):
    # Copy dv_guid from row2 to row1
    if "dv_guid" in row2:
        row1["dv_guid"] = row2["dv_guid"]
    return row1


# def compare_tables(sql_table, dataverse_table):
def compare_tables(sql_table, dataverse_table, primary_key):
    # Replace null values with empty strings in both tables
    if sql_table is None:
        sql_table = []

    sql_table = [replace_null_with_empty_string(row) for row in sql_table]
    dataverse_table = [replace_null_with_empty_string(row) for row in dataverse_table]

    # Extract primary key values from each table
    ids_sql_table = set(row[primary_key] for row in sql_table)
    ids_dataverse_table = set(row[primary_key] for row in dataverse_table)

    # Rows only in sql_table
    only_in_sql_table = [
        row for row in sql_table if row[primary_key] not in ids_dataverse_table
    ]

    # Rows only in dataverse_table
    only_in_dataverse_table = [
        row for row in dataverse_table if row[primary_key] not in ids_sql_table
    ]

    # Rows in both tables but with different values
    common_rows_diff_values = [
        copy_dv_guid(row1, row2)
        for row1 in sql_table
        for row2 in dataverse_table
        if row1[primary_key] == row2[primary_key]
        and not compare_rows(row1, row2, primary_key)
    ]

    return (
        only_in_sql_table,
        only_in_dataverse_table,
        common_rows_diff_values,
    )


@bp_compare_tables.route(route="comparetbl")
def comparetbl(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        sql_table = req_body.get("sql_table", [])
        dataverse_table = req_body.get("dataverse_table", [])
        primary_key = req_body.get("primary_key")

        (
            only_in_sql_table,
            only_in_dataverse_table,
            common_rows_diff_values,
        ) = compare_tables(sql_table, dataverse_table, primary_key)

        result = {
            "only_in_sql_table": only_in_sql_table,
            "only_in_dataverse_table": only_in_dataverse_table,
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

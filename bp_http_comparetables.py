import azure.functions as func
import logging
import json
import base64
import traceback
import io
import pandas as pd

bp_compare_tables = func.Blueprint()


def compare_tables(table1, table2):
    # Extract contest_ids from each table
    ids_table1 = set(row["contest_id"] for row in table1)
    ids_table2 = set(row["contest_id"] for row in table2)

    # Rows only in table1
    only_in_table1 = [row for row in table1 if row["contest_id"] not in ids_table2]

    # Rows only in table2
    only_in_table2 = [row for row in table2 if row["contest_id"] not in ids_table1]

    # Rows in both tables but with different values
    common_rows_diff_values = [
        row
        for row in table1
        if row in table2
        and row
        != next((r for r in table2 if r["contest_id"] == row["contest_id"]), None)
    ]

    # Rows in both tables that are the same
    common_rows_same_values = [
        row
        for row in table1
        if row in table2
        and row
        == next((r for r in table2 if r["contest_id"] == row["contest_id"]), None)
    ]

    return (
        only_in_table1,
        only_in_table2,
        common_rows_same_values,
        common_rows_diff_values,
    )


@bp_compare_tables.route(route="comparetbl")
def compare_tables(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        table1 = req_body.get("Table1", [])
        table2 = req_body.get("Table2", [])

        (
            only_in_table1,
            only_in_table2,
            common_rows_same_values,
            common_rows_diff_values,
        ) = compare_tables(table1, table2)

        result = {
            "only_in_table1": only_in_table1,
            "only_in_table2": only_in_table2,
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

import azure.functions as func
import json
import traceback

bp_get_lookup_guid = func.Blueprint()


def find_guid(data, lookup_column, alternate_key_column):
    for item in data:
        if item.get(alternate_key_column) == lookup_column:
            return item.get("gv_guid")
    return None


@bp_get_lookup_guid.route(route="getlookupguid")
def get_lookup_guid(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()

        # Check if required parameters are present in the request
        if "lookup_column" not in req_body or "data" not in req_body:
            return func.HttpResponse(
                "Invalid request. Missing required parameters.", status_code=400
            )

        lookup_column = req_body["lookup_column"]
        data = req_body["data"]

        # Check if data is in the correct format
        if not isinstance(data, list) or not data:
            return func.HttpResponse(
                "Invalid request. 'data' should be a non-empty list.", status_code=400
            )

        # Check if each item in the list has required columns
        for item in data:
            if (
                not isinstance(item, dict)
                or "gv_guid" not in item
                or "alternate_key_column" not in item
            ):
                return func.HttpResponse(
                    "Invalid request. Each item in 'data' should be a dictionary with 'gv_guid' and 'alternate_key_column'.",
                    status_code=400,
                )

        # Find the gv_guid based on lookup_column and alternate_key_column
        result_guid = find_guid(data, lookup_column, "alternate_key_column")

        # Return the result as a JSON response, even if it's null
        return func.HttpResponse(
            json.dumps({"result": result_guid}),
            mimetype="application/json",
            status_code=200,
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

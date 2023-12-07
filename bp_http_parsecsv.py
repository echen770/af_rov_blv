import azure.functions as func
import logging
import json
import base64
import traceback
import io
import pandas as pd

bp_parse_csv = func.Blueprint()


@bp_parse_csv.route(route="parsecsv")
def parse_csv(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        csv_base64 = req_body.get("csv_base64")

        if not csv_base64:
            return func.HttpResponse(
                "Please provide the 'csv_base64' in the request body.", status_code=400
            )

        # Decode the base64 string to bytes
        csv_bytes = base64.b64decode(csv_base64)

        # Parse the CSV data into a JSON
        try:
            csv_df = pd.read_csv(io.BytesIO(csv_bytes))
            json_data = csv_df.to_json(orient="records")
        except Exception as e:
            return func.HttpResponse(f"Error parsing CSV: {str(e)}", status_code=500)

        return func.HttpResponse(json_data, mimetype="application/json")

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

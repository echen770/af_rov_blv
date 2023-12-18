import azure.functions as func
import logging
import json
import base64
import traceback
import io
import pandas as pd

bp_set_office_title = func.Blueprint()


def process_office_titles(office_title_formulas, contest_snapshot):
    office_titles = []

    for contest_entry in contest_snapshot:
        office_id = contest_entry["office_id"]
        matching_formula = next(
            (
                item["formula"]
                for item in office_title_formulas
                if item["office_id"] == office_id
            ),
            None,
        )

        # if matching_formula is not None:
        #     concat_office_title = (
        #         matching_formula.replace("<bt1>", contest_entry["bt1"])
        #         .replace("<bt2>", contest_entry["bt2"])
        #         .replace("<bt3>", contest_entry["bt3"])
        #     )

        if matching_formula is not None:
            bt1 = contest_entry["bt1"] if contest_entry["bt1"] is not None else ""
            bt2 = contest_entry["bt2"] if contest_entry["bt2"] is not None else ""
            bt3 = contest_entry["bt3"] if contest_entry["bt3"] is not None else ""

            concat_office_title = (
                matching_formula.replace("<bt1>", bt1)
                .replace("<bt2>", bt2)
                .replace("<bt3>", bt3)
            )

            office_title = {
                "contest_snapshot_guid": contest_entry["contest_snapshot_guid"],
                "concat_office_title": concat_office_title,
                "office_id": office_id,
            }

            office_titles.append(office_title)

    return office_titles


@bp_set_office_title.route(route="setofficetitle")
def set_office_title(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()

        office_title_formulas = req_body.get("office_title_formulas", [])
        contest_snapshot = req_body.get("contest_snapshot", [])

        if not office_title_formulas or not contest_snapshot:
            return func.HttpResponse(
                "Invalid input. Both office_title_formulas and contest_snapshot arrays are required.",
                status_code=400,
            )

        result = process_office_titles(office_title_formulas, contest_snapshot)

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

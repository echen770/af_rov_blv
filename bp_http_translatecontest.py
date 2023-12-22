import azure.functions as func
import logging
import json
import traceback

bp_translate_contest = func.Blueprint()


def translate_contest(contest, glossary):
    for field in [
        "Ballot Title 1",
        "Ballot Title 2",
        "Ballot Title 3",
        "Banner",
        "Heading",
        "Concatenated Office Title",
    ]:
        if contest[field]:
            for glossary_entry in glossary:
                if (
                    glossary_entry["english_key"] == contest[field]
                    and glossary_entry["group_type"] == contest["group_type"]
                ):
                    contest[f"sp_{field}"] = glossary_entry["spanish_value"]
                    break  # Move to the next field after finding a match

    for field in ["Vote For", "sp_Vote For"]:
        if contest["vote_for_num"]:
            glossary_entry = next(
                (
                    entry
                    for entry in glossary
                    if entry["field_type"] == field
                    and entry["vote_for_num"] == int(contest["vote_for_num"])
                ),
                None,
            )
            if glossary_entry:
                contest[field] = glossary_entry["english_key"]
                contest[f"sp_{field}"] = glossary_entry["spanish_value"]

    return contest


@bp_translate_contest.route(route="translatecontest")
def translate_contest_snapshot(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        contest = req_body.get("contest", {})
        glossary = req_body.get("glossary", [])

        translated_contest = translate_contest(contest, glossary)

        return func.HttpResponse(
            json.dumps({"translated_contest": translated_contest}),
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

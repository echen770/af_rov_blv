import azure.functions as func
import logging
from bp_http_parsecsv import bp_parse_csv

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(bp_parse_csv)

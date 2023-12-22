import azure.functions as func
import logging
from bp_http_parsecsv import bp_parse_csv
from bp_http_comparetables import bp_compare_tables
from bp_http_setofficetitles import bp_set_office_title
from bp_http_getlookupguid import bp_get_lookup_guid
from bp_http_translatecontest import bp_translate_contest

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

app.register_functions(bp_parse_csv)
app.register_functions(bp_compare_tables)
app.register_functions(bp_set_office_title)
app.register_functions(bp_get_lookup_guid)
app.register_functions(bp_translate_contest)

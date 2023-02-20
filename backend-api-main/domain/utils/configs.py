import os
from jsql import sql
from db.base import engine
from domain.utils.enums import Severity
from domain.utils.logging import log_message
from domain.utils.general import read_public_google_sheet
from domain.utils.enums import ConfigKey

# ToDo
SHEET_ID = os.getenv("CONFIGS_SHEET_ID", '1iu_aH6YL7lWaoO_jfouj7D4Mxa2YLsgYXnMK0SZ7MxY')
SHEET_NAME = os.getenv("CONFIGS_SHEET_NAME", 'Configurations')


CONFIGS = None

def refresh_configs():
    global CONFIGS
    NEW_CONFIGS = {}
    # todo, try catch on whole block:
    doc = read_public_google_sheet(SHEET_ID, SHEET_NAME)
    for i in doc["key"].keys():
        key = doc["key"][i]
        val = str(doc["val"][i])
        type = doc["type"][i]
        val = val.removeprefix("xx")
        if type == "int": val = int(val)
        elif type == "str-list": val = val.split(",")
        elif type == "int-list":
            split = val.split(",")
            val = [int(v) for v in split]

        if not val and val != 0: return False
        try:
            NEW_CONFIGS[ConfigKey[key].value] = val
        except:
            log_message(f"failed to refresh configs key {key}")
    
    CONFIGS = NEW_CONFIGS
    log_message("refreshing configs done")


def get_config(key: ConfigKey):
    if CONFIGS is None:
        refresh_configs()
    return CONFIGS[key.value]













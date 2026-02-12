# All global variables
import re
#Define allowed values and required fields
REQUIRED_FIELDS = [
    "study_id", "study", "lab_id", "redcap_event_name", "sampling_date", "biomaterial", "tube_pos",
    "redcap_repeat_instrument", "redcap_repeat_instance", 
    "tube_id", "box_id", "freezer", "rack", "box", "tube_status", 
]

#Valid Biomaterial in aliquots
VALID_MATERIALS = [
    "csf", "csf pellet", "dna", "edta plasma", "fibroblasten",
    "paxgene", "pbmc", "serum", "urin"
]

BIOFLUIDS = ["Urin", "EDTA Plasma", "Serum", "CSF", "CSF Pellet"]
DNA = ["DNA"]
PAXGENE =  ["PAXgene"]
CELLS = ["Fibroblasten", "PBMC"]

#Study_id pattern is in the order XXX-XXX-XXX with x being a natural number
STUDY_ID_PATTERN = re.compile(r"^\d{3}-\d{3}-\d{3}$") #d means here digit betwenn 0-9

#Valid redcap events/ #Redcap event name stellvertretend für Arm der Studie
VALID_EVENTS = ["baseline_arm_1", "screening_arm_1", "follow_up_arm_1"]
#Das muss noch verändert werden

VALID_tube_status = [""]

#Allowed matrices (positions) per biomaterial
VALID_POS_FLUIDS = [f"{row}{col}" for row in "ABCDEFGH" for col in range(1, 13)]
VALID_POS_PAXGENE = [f"{row}{col}" for row in "ABCDEFG" for col in range(1, 8)]
VALID_POS_DNA_CELLS_PBMC =  [f"{row}{col}" for row in "ABCDEFGHJ" for col in range(1, 11)]

#Freezers
VALID_FREEZER = ["1", "2", "3", "nitrogen", "4deg"]

#Boxes (same for all, unless exception later)
VALID_BOX = [str(i) for i in range(1, 43)]  # 1–42

#Racks
VALID_RACK = [str(i) for i in range(1, 101)]  # 1–100

#Storage Rules for the availability check up
STORAGE_RULES = {
    "BIOFLUID": {
        "freezers": ["1", "2", "3"],
        "racks": list(map(str, range(1, 8))),   # 1–7
        "boxes_per_rack": 7,
        "rows": list("ABCDEFGH"),
        "cols": list(map(str, range(1, 13))),   # 1–12
    },

    "PAXGENE": {
        "freezers": ["1", "2", "3"],
        "racks": list(map(str, range(1, 8))),
        "boxes_per_rack": 7,
        "rows": list("ABCDEFG"),
        "cols": list(map(str, range(1, 8))),    # 1–7
    },

    "DNA": {
        "freezers": ["4deg"],
        "racks": list(map(str, range(1, 8))),
        "boxes_per_rack": 7,
        "rows": list("ABCDEFGHIJ"),
        "cols": list(map(str, range(1, 11))),   # 1–10
    },

    "CELLS": {
        "freezers": ["nitrogen"],
        "racks": list(map(str, range(1, 8))),   # assumption for now
        "boxes_per_rack": 14,                   # boxnum fortlaufend
        "rows": list("ABCDEFGHIJ"),
        "cols": list(map(str, range(1, 11))),
    },
}


FREEZER_ORDER = {
    "1": 1,
    "2": 2,
    "3": 3,
    "4deg": 4,
    "nitrogen": 5,
}



# Here the API TOKEN of SOPHIE need to go inside and the url for RD registry # this needs to be unvisable once you are ready
API_URL = "https://redcap.uni-heidelberg.de/api/"

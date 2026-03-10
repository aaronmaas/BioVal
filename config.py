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
    "paxgene", "pbmc", "serum", "urine"
]

#The numbers represent the corresponding code for redcap for a given material
BIOFLUIDS = ["urine", "Urine" , "EDTA Plasma", "edta plasma", "Serum", "serum", "CSF","csf", "CSF Pellet", "csf pellet",
            "1", "2", "3", "7", "8"]
DNA = ["DNA", "dna", "4" ]
PAXGENE =  ["PAXgene", "paxgene", "5"]
CELLS = ["Fibroblasten", "PBMC", "fibroblasten", "pbmc", "6", "9"]

REDCAP_EVENT_NAME = ["participant_regist_arm_1"]
REDCAP_REPEAT_INSTRUMENTS = ["biorepository"]

VALID_TUBE_STATUS = ["1", "2", "3", "4", "5"]

#Study_id pattern is in the order XXX-XXX-XXX with x being a natural number
#STUDY_ID_PATTERN = re.compile(r"^\d{3}-\d{3}-\d{3}$") #d means here digit betwenn 0-9 also Xs must be allowed
STUDY_ID_PATTERN = re.compile(r'^[0-9X]{3}-[0-9X]{3}-[0-9X]{3}$')

#Allowed matrices (positions) per biomaterial
VALID_POS_FLUIDS = [f"{row}{col}" for row in "ABCDEFGH" for col in range(1, 13)]
VALID_POS_PAXGENE = [f"{row}{col}" for row in "ABCDEFG" for col in range(1, 8)]
VALID_POS_DNA_CELLS_PBMC =  [f"{row}{col}" for row in "ABCDEFGHIJ" for col in range(1, 11)]

#Freezers
VALID_FREEZER = ["1", "2", "3", "nitrogen", "4deg"]

#Boxes (same for all, unless exception later)
VALID_BOX = [str(i) for i in range(1, 43)]  # 1–42

#Racks # this cannot be same for all but is now
VALID_RACK = [str(i) for i in range(1, 101)]  # 1–100

#Storage Rules for the availability check up
STORAGE_RULES = {
    "BIOFLUID": {
        "freezers": ["1", "2", "3"],
        "racks": list(map(str, range(1, 8))),   # 1–7
        "boxes_per_rack": 42,
        "rows": list("ABCDEFGH"),
        "cols": list(map(str, range(1, 13))),   # 1–12
    },

    "PAXGENE": {
        "freezers": ["1", "2", "3"],
        "racks": list(map(str, range(1, 8))),
        #"boxes_per_rack": 7,
        "rows": list("ABCDEFG"),
        "cols": list(map(str, range(1, 8))),    # 1–7
    },

    "DNA": {
        "freezers": ["4deg"],
        "racks": list(map(str, range(1, 8))),
        #"boxes_per_rack": 7,
        "rows": list("ABCDEFGHIJ"),
        "cols": list(map(str, range(1, 11))),   # 1–10
    },

    #"CELLS": {
    #    "freezers": ["nitrogen"],
    #    "racks": list(map(str, range(1, 8))),   # assumption for now
    #    "boxes_per_rack": 14,                   # boxnum fortlaufend
    #    "rows": list("ABCDEFGHIJ"),
    #    "cols": list(map(str, range(1, 11))),
    #},
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

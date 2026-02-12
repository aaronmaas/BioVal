from config import REQUIRED_FIELDS, VALID_POS_PAXGENE, VALID_POS_FLUIDS, VALID_POS_DNA_CELLS_PBMC, VALID_RACK
from config import BIOFLUIDS, CELLS, DNA, PAXGENE, VALID_BOX, STUDY_ID_PATTERN
from utils import read_csv


def check_structure(headers):
    """
    Validation function. Checks whether all required fields are present in the CSV headers.

    Args:
        headers (List[str]): Column headers from the CSV

    Returns:
        List[str]: List of missing required fields (if any)
    """
    missing = [field for field in REQUIRED_FIELDS if field not in headers]
    return missing


def validate_row(row, index):
    """
    Validation function. Validates a single row for required values and correct formats if needed.
    The validation process can be done for any type of data - to be uploaded ones or the RedCap Reference
    data. 
    
    Steps: 
    (1) Checks again for the Required fields (it does that to safe it as error message)
    (2) Checks the materialspecific storage rules. Checks 
    (3) 
    Args:
        row (Dict): A row from the CSV as a dictionary
        index (int): The row number (for error reporting)

    Returns:
        errors List[str]: List of validation error messages for this row
    """
    errors = []

    # (1) Required fields
    for field in REQUIRED_FIELDS:
        if row.get(field, "").strip() == "":
            errors.append(f"Row {index}: Missing value in '{field}'")
    # (2) Checks the Biomaterialspecific storage rules
    # Get material 
    biomaterial = row.get("biomaterial", "").strip().lower()
    tube_pos = row.get("tube_pos", "").strip()
    freezer = row.get("freezer", "").strip()
    rack = row.get("rack", "").strip()
    box = row.get("box", "").strip()
    #  Material-specific storage rules - safe in errors if there is a mistake
    if biomaterial in BIOFLUIDS:  # fluids
        if tube_pos not in VALID_POS_FLUIDS:
            errors.append(f"Row {index}: Invalid tube-pos '{tub_pos}' for {biomaterial} (must be A1–H10)")
        if freezer not in ["1", "2", "3"]:
            errors.append(f"Row {index}: {biomaterial} must be stored in -80 freezers (1–3).")

    elif biomaterial in PAXGENE:
        if tube_pos not in VALID_POS_PAXGENE:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for PAXgene (must be A1–G7)")
        if freezer not in ["1", "2", "3"]:
            errors.append(f"Row {index}: PAXgene must be stored in -80 freezers (1–3).")

    elif biomaterial in DNA:
        if tube_pos not in VALID_POS_DNA_CELLS_PBMC:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for DNA (must be A1–J10)")
        if freezer != "4deg":
            errors.append(f"Row {index}: DNA must be stored in 4-degree freezer.")

    elif biomaterial in CELLS:
        if tube_pos not in VALID_POS_DNA_CELLS_PBMC:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for {biomaterial} (must be A1–J10)")
        if freezer != "nitrogen":
            errors.append(f"Row {index}: {biomaterial} must be stored in nitrogen tank.")
    #Eception
    else:
        errors.append(f"Row {index}: Unknown or unsupported material '{biomaterial}'")
        
    # Please hier noch den Check einfügen für den Tube_status

    # General checks still valid - hier muss eigentlich unterschieden werden zwischen Racks 
    # da z.B. cells ja in den Tank gehen und da ist die Struktur anders
    if rack and rack not in VALID_RACK:
        errors.append(f"Row {index}: Invalid rack '{rack}'")

    if box and box not in VALID_BOX:
        errors.append(f"Row {index}: Invalid box '{box}'")

    return errors


def validate_file(path, label):
    """
    Core function from GUI. Validates an entire CSV file and raises ValueError if anything is wrong. The validation
    is done line by line.
    
    Args:
        path (str): Path to the CSV file
        label (str): Descriptive label (e.g. "Import file")

    Returns:
        rows List[dict]: List of rows from the to be validated file. The row is handeled like a dictionary.
    """
    print(f" Checking {label}: {path}")
    headers, rows = read_csv(path)
    
    # Check for required column headers - so in the document not on the 
    structure_errors = check_structure(headers)
    if structure_errors:
        raise ValueError(f"Missing required columns in {label}: {structure_errors}")
    #errors hier definieren und dann mitgeben anstatt den Validation check for required columns doppelt zu machen
    for i, row in enumerate(rows, start=2):
        validate_row(row, i)  # will raise immediately if invalid

    print(f" {label} passed all validation checks.\n")
    return rows  # return rows if valid

def check_duplicate_positions(import_rows, occupied_positions, label="Import vs Reference"):
    """
    Core function from GUI. Compares import rows against existing positions and raises errors for conflicts.

    Args:
        import_rows (List[Dict]): Rows from the import file
        occupied_positions (Set[Tuple]): Set of existing (freezer, rack, box, pos)
        label (str): Descriptive name for error reporting

    Raises:
        ValueError: if duplicate positions are found or 0 if none are found
    """
    errors = []
    for i, row in enumerate(import_rows, start=2):
        key = (
            row.get("freezer", "").strip(),
            row.get("rack", "").strip(),
            row.get("box", "").strip(),
            row.get("tube_pos", "").strip(),
        )
        if key in occupied_positions:
            errors.append(f"Row {i}: Position {key} is already occupied in reference data.")

    if errors:
        raise ValueError(f"{label} – {len(errors)} duplicate position error(s):\n" + "\n".join(errors))
    else:
        print(f"No duplicate positions found between import and reference data.")
        return 0

    
def check_internal_duplicates(rows, label):
    """
    Core function in GUI. Checks for duplicate positions within a single file.

    Args:
        rows (List[Dict]): Rows to check
        label (str): Descriptive name for error output

    Returns:
        ValueError: if internal duplicates found otherwise returns
    """
    position_map = {}

    for i, row in enumerate(rows, start=2):  # row index starts from line 2
        key = (
            row.get("freezer", "").strip(),
            row.get("rack", "").strip(),
            row.get("box", "").strip(),
            row.get("tube_pos", "").strip(),
        )

        if all(key):
            position_map.setdefault(key, []).append(i)

    # Look for positions used more than once
    duplicates = {k: v for k, v in position_map.items() if len(v) > 1}
    
    # Duplicates Handling
    if duplicates: 
        details = "\n".join([f" - Position {k} found on rows {v}" for k, v in duplicates.items()])
        raise ValueError(f"Duplicate positions found within {label}:\n{details}")
    else:
        print(f"No duplicate positions found within {label}.")
        
    return 
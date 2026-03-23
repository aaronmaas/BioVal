from config import REQUIRED_FIELDS, VALID_POS_PAXGENE, VALID_POS_FLUIDS, VALID_POS_DNA_CELLS_PBMC, VALID_RACK
from config import BIOFLUIDS, CELLS, DNA, PAXGENE, VALID_BOX, STUDY_ID_PATTERN, REDCAP_EVENT_NAME, REDCAP_REPEAT_INSTRUMENTS, VALID_TUBE_STATUS
from utils import read_csv
from utils import make_instance_key


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
    redcap_event_name = row.get("redcap_event_name","").strip()
    redcap_repeat_instrument = row.get("redcap_repeat_instrument","").strip()
    redcap_repeat_instance = row.get("redcap_repeat_instance","").strip()
    tube_status = row.get("tube_status", "").strip()
    study_id = row.get("study_id", "").strip()
    box_id = row.get("box_id","").strip()
    

    # SKIP LOGIC: leere REDCap-Zeilen in ref_file ignorieren
    if not biomaterial and not redcap_repeat_instrument and not tube_pos:
        return []
   
    # Check if redcap_event_name is in RDregistry
    if redcap_event_name not in REDCAP_EVENT_NAME:
        errors.append(f"Row {index}: Invalid Redcap Event name must be participant_regist_arm_1.")
    
    if redcap_repeat_instrument not in REDCAP_REPEAT_INSTRUMENTS:
        errors.append(f"Row {index}: Invalid Redcap Repeated instrument: must be biorepository.")
    
    if redcap_repeat_instance:
        if not redcap_repeat_instance.isdigit():
            errors.append(
                f"Row {index}: redcap_repeat_instance must be a positive integer"
            )
        elif int(redcap_repeat_instance) <= 0:
            errors.append(
                f"Row {index}: redcap_repeat_instance must be >= 1"
            )
            
    print(tube_pos)
    # Unfortunately its different for the upload and import file!
    #  Material-specific storage rules - safe in errors if there is a mistake
    if biomaterial in BIOFLUIDS:  # fluids
        if tube_pos not in VALID_POS_FLUIDS:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for {biomaterial} (must be A1–H10)")
        if freezer not in ["1", "2", "3"]:
            errors.append(f"Row {index}: {biomaterial} must be stored in -80 freezers (1–3).")
        if rack not in VALID_RACK: 
            errors.append(f"Row {index}: Invalid rack number '{rack}' for {biomaterial} (must be 1-100)")
        if box not in VALID_BOX: 
            errors.append(f"Row {index}: Invalid box number '{box}' for {biomaterial} (must be 1-1000)")
        if not box_id: 
            errors.append(f"Row {index}: Invalid box or empty box ID '{box_id}' for {biomaterial} (must be unique ID)")

    elif biomaterial in PAXGENE:
        if tube_pos not in VALID_POS_PAXGENE:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for PAXgene (must be A1–G7)")
        if freezer not in ["1", "2", "3"]:
            errors.append(f"Row {index}: PAXgene must be stored in -80 freezers (1–3).")
        if box not in range(1,501):  #das als string!
            errors.append(f"Row {index}: Invalid box number '{box}' for {biomaterial} (must be 1-500)")
        if rack:
            errors.append(f"Row {index}: Rack must be empty for {biomaterial}") 
        if box_id:   
            errors.append(f"Row {index}: Box ID must be empty for {biomaterial}") 


    elif biomaterial in DNA:
        if tube_pos not in VALID_POS_DNA_CELLS_PBMC:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for DNA (must be A1–J10)")
        if freezer != "4": #here I need to be careful because this is exactly the problem
            errors.append(f"Row {index}: DNA must be stored in 4-degree freezer.")
        if rack:
            errors.append(f"Row {index}: Rack must be empty for {biomaterial}") 
        if box_id:   
            errors.append(f"Row {index}: Box ID must be empty for {biomaterial}")

    ####evtl brauche ich cells nicht                  
    elif biomaterial in CELLS:
        if tube_pos not in VALID_POS_DNA_CELLS_PBMC:
            errors.append(f"Row {index}: Invalid tube-pos '{tube_pos}' for {biomaterial} (must be A1–J10)")
        if freezer != "5": #here I need to be careful because this is exactly the problem
            errors.append(f"Row {index}: {biomaterial} must be stored in nitrogen tank.")
        if box_id:   
            errors.append(f"Row {index}: Box ID must be empty for {biomaterial}")
        if rack not in range(1,101): 
            errors.append(f"Row {index}: Invalid rack number '{rack}' for {biomaterial} (must be 1-100)")
                                               
                          
    #Eception
    else:
        errors.append(f"Row {index}: Unknown or unsupported material '{biomaterial}'")
   
    # General checks
    if tube_status not in VALID_TUBE_STATUS: 
        errors.append(f"Row {index}: Invalid tube_status '{tube_status}' for {biomaterial} (must be 1-5)")   
        
    if not study_id:
        errors.append(f"Row {index}: Missing study_id")

    elif not STUDY_ID_PATTERN.fullmatch(study_id):
        errors.append(f"Row {index}: Invalid study_id format '{study_id}'")
        
    #print(
    #"DEBUG study_id:",
    #repr(study_id),
    #"match:",
    #bool(STUDY_ID_PATTERN.fullmatch(study_id)))

    return errors


def validate_reference_file(path, label):
    """
    Core function from GUI. Validates an entire CSV file and raises ValueError if anything is wrong. The validation
    is done line by line.
    
    Args:
        path (str): Path to the CSV file
        label (str): Descriptive label (e.g. "Reference File")

    Returns:
        rows List[dict]: List of rows from the reference file. The row is handeled like a dictionary.
    """
    errors_list = []
    print(f" Checking {label}: {path}")
    headers, rows = read_csv(path)
    
    # Check for required column headers - in validate row its done again so it can be passed to erros
    structure_errors = check_structure(headers)
    if structure_errors:
        raise ValueError(f"Missing required columns in {label}: {structure_errors}")
    
    for i, row in enumerate(rows, start=2):
        errors_list.append(validate_row(row, i))  # will raise immediately if invalid; here errors need to be passed out! 
        #otherwise the report will not see the errors!

    ### Here fehlt aktuell der raise der validation checks das sollte ich morgen mit sophie besprechen
    print(f" {label} passed all validation checks.\n")
    return rows, errors_list  # return rows if valid; das ergibt keinen sinn? wofür gebe ich den rows zurück? habe das 
    #jetzt mal raus genommen
    
def validate_import_file(path, label, reference_rows):
    """
    Core function from GUI. Validates the import CSV file and raises ValueError if anything is wrong. The validation
    is done line by line and for the tubeinstances accross the whole file. 
    
    Args:
        path (str): Path to the CSV file
        label (str): Descriptive label (e.g. "Import file")
        reference_rows List[Dict]: Reference rows from previous call of validate_reference_file.  

    Returns:
        rows List[dict]: List of rows from the to be validated file. The row is handeled like a dictionary.
    """
    
    headers, rows = read_csv(path)

    # 1. structure
    structure_errors = check_structure(headers)
    if structure_errors:
        raise ValueError(f"Missing required columns in {label}: {structure_errors}")
    
    # 2. row-level validation
    all_row_errors = []
    for i, row in enumerate(rows, start=2):
        all_row_errors.extend(validate_row(row, i))

    # 3. dataset-level validation
    instance_errors = validate_tube_instances(
        import_rows=rows,
        reference_rows=reference_rows
    )

    all_errors = all_row_errors + instance_errors + structure_errors

    #if all_errors:
    #    raise ValueError(all_errors) ####

    return rows, all_errors

#### outdated validate_file because I am doing the check differently now
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


def validate_tube_instances(import_rows, reference_rows):
    """
    Validation function. Validates import and ref files for the instances. It is of
    utter importance that for each patient the RedCap instances are unique. 

    Args:
        import_rows (Dict): Imported rows from import file
        ref_rows (Dict): Reference rows from RedCap Download.

    Returns:
        errors List[str]: List of instance validation error messages in total. 
    """
    errors = []

    ref_instances = set()
    for row in reference_rows:
        key = make_instance_key(row)
        if all(key):
            ref_instances.add(key)
    seen_import_instances = set()

    for idx, row in enumerate(import_rows, start=1):
        key = make_instance_key(row)

        if not all(key):
            continue  #fehlende Felder werden anderswo geprüft

        study_id, instance = key

        #Doppelt im Importfile (pro Patient!)
        if key in seen_import_instances:
            errors.append(
                f"Row {idx}: Duplicate tube instance {instance} "
                f"for patient {study_id} in import file."
            )
        else:
            seen_import_instances.add(key)

        #Überschreiben verhindern
        if key in ref_instances:
            errors.append(
                f"Row {idx}: Tube instance {instance} for patient {study_id} "
                f"already exists in REDCap and must not be overwritten."
            )
    print(errors)
    return errors




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
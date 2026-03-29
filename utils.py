import csv
from config import STUDY_ID_PATTERN
from datetime import datetime


def read_csv(path):
    """
    Helper function. Reads a CSV file and returns its headers and row data.

    Args:
        path (str): Path to the CSV file

    Returns:
        tuple: (List[str] headers, List[Dict] rows)
    """
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return reader.fieldnames, rows

def make_instance_key(row):
    """
    Helper function. Generates key for the instance validation.

    Args:
        row (list): List of data for specific row in import or reference. 

    Returns:
        Tupel: [Study_id(XXX-XXX-XXX), redcap_repeat_instance(int)] 
    """
    return (
        row.get("study_id", "").strip(),
        row.get("redcap_repeat_instance", "").strip(),
    )          
            
def write_report(filename, import_file, import_rows, reference_file, 
                 error_input, error_reference, labid_messages = None, instance_messages = None, recommendation=None):
    """
    Writes a validation report to a text file.

    Args:
        filename (str): Path to save the report
        import_file (str): Path to import CSV
        reference_file (str): Path to reference CSV
        import_rows (List[Dict], optional): Imported rows, for summary stats
        errors (List[str], optional): List of error messages collected
        recommendation (str, optional): Recommendation to upload or not
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Biorepository Data Validation Report\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("="*50 + "\n\n")

        f.write("Input files:\n")
        f.write(f" - Import: {import_file}\n")
        f.write(f" - Reference: {reference_file}\n\n")

        # Summary
        f.write("Summary:\n")
        if import_rows:
            f.write(f" - Number of import rows processed: {len(import_rows)}\n")
        f.write("\n")

        # Errors Input file
        f.write("Errors / Warnings Inputfile:\n")
        if error_input and len(error_input) > 0:
            for e in error_input:
                f.write(f" - {e}\n")
        else:
            f.write(" - None\n")
        f.write("\n")
        
        # Lab Id assignment
        f.write("Lab Id assignment ")
        if labid_messages: 
            for msg in labid_messages:
                f.write(f" - {msg}\n")
        else:
            f.write(" - None\n")
        f.write("\n")
        
        # Instance assignment
        f.write("Red cap instance assignment \n")
        if instance_messages: 
            for msg in instance_messages:
                f.write(f" - {msg}\n")
        else:
            f.write(" - None\n")
        f.write("\n")
        
        # Errors Reference file
        f.write("Errors / Warnings Referencefile:\n")
        if error_reference and len(error_reference) > 0:
            for error_list in error_reference:
                if not error_list:
                    continue

                row_prefix = error_list[0].split(":")[0]  # splitting rows
                f.write(f"\n{row_prefix}:\n")

                for error in error_list:
                    message = error.split(":", 1)[1].strip()
                    f.write(f"  - {message}\n")
            
            #for e in error_reference:
            #    f.write(f" - {e}\n")
        else:
            f.write(" - None\n")
        f.write("\n")
        
        
        
        # Recommendation
        #f.write("Recommendation:\n")
        #if recommendation:
        #    f.write(f"{recommendation}\n")
        #else:
        #    f.write("No recommendation provided.\n")
            
            
def save_data_as_csv(records, out_path):
    """
    Helper function from GUI. Safes data from to csv at out_path.

    Args:
        records List[Dict]: A list of flat REDCap records
        out_path (str): Storage path
    """
    if not records:
        raise Exception("No records to write.")

    keys = records[0].keys() #without sorted otherwise it is alphabetic
    
    #['study_id', 'redcap_event_name','redcap_repeat_instance','redcap_repeat_instrument','lab_id','study','sampling_date','biomaterial','volume_cell_number','tube_id','box_id','tube_pos','box','rack','freezer','tube_status','fibro_passage','sent_date','sent_project','reserved_date','reserved_for','comment','biorepository_complete']

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(records)

    print(f"Data saved to {out_path}")
    
def build_patient_map(reference_rows):
    """
    Helper function. Builds study_id → lab_patient_id mapping from REDCap reference data.
    
    study_to_lab 
    
    Args:
        refernce_rows: records form Reference Dataset. Usually csv file.

    Returns:
        study_to_lab List[Dict]: Mapping from study_id -> pat_id
        lab_to_study List[Dict]: Mapping from lab_id -> study_id
        used_lab_ids List: list of used lab ids. 
    """

    study_to_lab = {}
    lab_to_study = {}
    used_lab_ids = set()

    for row in reference_rows:
        study_id = row.get("study_id", "").strip()
        lab_id = row.get("lab_id", "").strip()

        if not study_id or not lab_id:
            continue
         
        if study_id in study_to_lab and study_to_lab[study_id] != lab_id:
            raise Exception(f"Study ID {study_id} has multiple lab IDs.")

        if lab_id in lab_to_study and lab_to_study[lab_id] != study_id:
            raise Exception(f"Lab ID {lab_id} is linked to multiple study IDs.")

        lab_to_study[lab_id] = study_id
        study_to_lab[study_id] = lab_id
        used_lab_ids.add(int(lab_id))

    return study_to_lab, lab_to_study, used_lab_ids

def get_next_lab_patient_id(used_lab_ids):
    """
    Helper function. Gets next available Lab ID.
    
    Args:
        used_lab_ids List: list of used lab ids. 
    Returns:
        Float: next available Lab ID 
    """
    #vielleicht sollte ich hier lieber einen string testen? ich will ja 00001 und nicht 1 
    if not used_lab_ids:
        return 1
    return max(used_lab_ids) + 1

def assign_lab_patient_ids(import_rows, reference_rows):
    """
    Core function from Gui. Assigns lab_id based on study_id and reference data. The lab id does not need to be plugged in; 
    BioVal finds the last lab id in the reference data and automatically asigns to the to be importated
    data the new lab id. 
    
    Args:
    
    Returns:
    
    """
    # !!!!!!!!!!!!!!! Make absolutley sure, that the labID is never filled in; also wenn mal eine "frei" wird sozusagen
    study_to_lab, lab_to_study, used_lab_ids = build_patient_map(reference_rows)
    next_id = get_next_lab_patient_id(used_lab_ids)
    labid_messages = [f"Next available lab patient ID: {next_id:05d}"]

    #ich checke hier actuell nur die imported rows! 
    for i, row in enumerate(import_rows, start=2):
        study_id = row.get("study_id", "").strip()

        if study_id in study_to_lab:
            row["lab_id"] = study_to_lab[study_id]
        else:
            lab_id = f"{next_id:05d}"
            row["lab_id"] = lab_id
            study_to_lab[study_id] = lab_id
            used_lab_ids.add(next_id)
            next_id += 1
            labid_messages.append(
                f"Assigned lab patient ID {lab_id} to study ID {study_id}")
    
    return import_rows, labid_messages



def build_instance_maps_old(reference_rows):
    """
    Helper function. Builds necessary maps for red cap instances. One tube correponds to one red cap instance. Finds the maximum instance number for each study id such that an autoincrement can be performed for future instances.
    
    args
        refernce_rows: records form Reference Dataset. Usually csv file.
    Returns:
        study_to_max_instance LIST[Dict]: Mapping from study_id -> max instance
        tube_map LIST[Dict]: Mapping from study_id and tube_id -> max instance
    """
    study_to_max_instance = {}
    tube_map = {}

    for row in reference_rows:
        study_id = row.get("study_id", "").strip()
        #print("1 okay")
        instance = str(row.get("redcap_repeat_instance", "")).strip()
        #print("2 okay")
        tube_id = row.get("tube_id", "").strip()
        #print("3 okay")

        if not study_id or not instance:
            continue

        instance = int(instance)

        # track max instance per patient
        # necessary because more rows than patients
        if study_id not in study_to_max_instance:
            study_to_max_instance[study_id] = instance
        else:
            study_to_max_instance[study_id] = max(
                study_to_max_instance[study_id], instance
            )

        # track tube → instance
        if tube_id:
            tube_map[(study_id, tube_id)] = instance

    return study_to_max_instance, tube_map


def build_instance_maps(reference_rows):
    study_to_max_instance = {}
    tube_map = {}

    for row in reference_rows:
        study_id = str(row.get("study_id", "")).strip()
        instance = str(row.get("redcap_repeat_instance", "")).strip()

        if not study_id or not instance:
            continue

        instance = int(instance)

        # track max instance per study_id
        study_to_max_instance[study_id] = max(
            study_to_max_instance.get(study_id, 0),
            instance
        )

        # --- build tube identifier ---
        tube_id = str(row.get("tube_id", "")).strip()

        if tube_id:
            tube_key = tube_id
        else:
            freezer = str(row.get("freezer", "")).strip()
            rack = str(row.get("rack", "")).strip()
            box = str(row.get("box", "")).strip()
            pos = str(row.get("tube_pos", "")).strip()

            # only use position if complete
            if all([freezer, rack, box, pos]):
                tube_key = (freezer, rack, box, pos)
            else:
                continue  # cannot identify tube reliably

        tube_map[(study_id, tube_key)] = instance

    return study_to_max_instance, tube_map

def assign_instances(import_rows, reference_rows):
    study_to_max, tube_map = build_instance_maps(reference_rows)

    messages = []

    for i, row in enumerate(import_rows, start=2):
        study_id = str(row.get("study_id", "")).strip()

        if not study_id:
            raise Exception(f"Row {i}: Missing study_id")

        # --- build tube identifier ---
        tube_id = str(row.get("tube_id", "")).strip()

        if tube_id:
            tube_key = tube_id
        else:
            freezer = str(row.get("freezer", "")).strip()
            rack = str(row.get("rack", "")).strip()
            box = str(row.get("box", "")).strip()
            pos = str(row.get("tube_pos", "")).strip()

            if all([freezer, rack, box, pos]):
                tube_key = (freezer, rack, box, pos)
            else:
                raise Exception(
                    f"Row {i}: Cannot identify tube (no tube_id and incomplete position)"
                )

        key = (study_id, tube_key)

        # CASE 1: existing tube → reuse instance
        if key in tube_map:
            instance = tube_map[key]
            row["redcap_repeat_instance"] = str(instance)

            messages.append(
                f"Row {i}: Reused instance {instance} for existing tube"
            )

        # CASE 2: new tube → assign next instance
        else:
            next_instance = study_to_max.get(study_id, 0) + 1

            row["redcap_repeat_instance"] = str(next_instance)

            study_to_max[study_id] = next_instance
            tube_map[key] = next_instance

            messages.append(
                f"Row {i}: Assigned new instance {next_instance} to study {study_id}"
            )

    return import_rows, messages


def assign_instances_old(import_rows, reference_rows):
    #print("Okay 1")
    study_to_max, tube_map = build_instance_maps(reference_rows)
    messages = []

    for i, row in enumerate(import_rows, start=2):
        study_id = row.get("study_id", "").strip()
        tube_id = row.get("tube_id", "").strip()
        #print("Okay")
        if not study_id:
            raise Exception(f"Row {i}: Missing study_id")

        # CASE 1: Tube already exists → reuse instance
        if (study_id, tube_id) in tube_map:
            instance = tube_map[(study_id, tube_id)]
            row["redcap_repeat_instance"] = str(instance)

            messages.append(
                f"Row {i}: Existing tube → reused instance {instance}"
            )

        # CASE 2: New tube → assign next instance
        else:
            next_instance = study_to_max.get(study_id, 0) + 1

            row["redcap_repeat_instance"] = str(next_instance)

            study_to_max[study_id] = next_instance
            tube_map[(study_id, tube_id)] = next_instance

            messages.append(
                f"Row {i}: Assigned new instance {next_instance} to patient {study_id}"
            )

    return import_rows, messages
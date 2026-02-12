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


def write_report(filename, import_file, reference_file, labid_messages =None, import_rows=None,
                 errors=None, recommendation=None):
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

        # Errors
        f.write("Errors / Warnings:\n")
        if errors and len(errors) > 0:
            for e in errors:
                f.write(f" - {e}\n")
        else:
            f.write(" - None\n")
        f.write("\n")
        
        # Lab Id assignment
        f.write("Lab Id assignment")
        if labid_messages: 
            for msg in labid_messages:
                f.write(f" - {msg}\n")
        else:
            f.write(" - None\n")
        f.write("\n")
        
        # Recommendation
        f.write("Recommendation:\n")
        if recommendation:
            f.write(f"{recommendation}\n")
        else:
            f.write("No recommendation provided.\n")
            
            
def save_data_as_csv(records, out_path):
    """
    Helper function from GUI. Safes data from to csv at out_path.

    Args:
        records List[Dict]: A list of flat REDCap records
        out_path (str): Storage path
    """
    if not records:
        raise Exception("No records to write.")

    keys = sorted(records[0].keys())

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

        if not study_id:
            raise Exception(f"Row {i}: Missing study_id")

        if not STUDY_ID_PATTERN.match(study_id):
            raise Exception(f"Row {i}: Invalid study_id format '{study_id}'")

        if study_id in study_to_lab:
            row["lab_id"] = study_to_lab[study_id]
        else:
            lab_id = f"{next_id:05d}"
            row["lab_id"] = lab_id
            study_to_lab[study_id] = lab_id
            used_lab_ids.add(next_id)
            next_id += 1
            labid_messages.append(
                f"Assigned lab patient ID {lab_id} to study ID {study_id}"
            )

    return import_rows, labid_messages
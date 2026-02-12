from config import STORAGE_RULES, FREEZER_ORDER, STUDY_ID_PATTERN
from itertools import product
import csv
from collections import defaultdict



def get_occupied_positions(rows):
    """
    Core function from GUI. Extracts all occupied positions from a list of data rows, only if
    they match the tube_status stored. 

    Args:
        rows (List[Dict]): Data rows (e.g. from reference file)

    Returns:
        positions Set[Tuple[str, str, str, str]]: Set of (freezer, rack, box, pos)
    """
    positions = set()

    for row in rows:
        status = row.get("tube_status", "").strip()

        # Only "Stored" tubes occupy a position
        if status != "1":
            continue

        key = (
            row.get("freezer", "").strip(),
            row.get("rack", "").strip(),
            row.get("box", "").strip(),
            row.get("tube_pos", "").strip(),
        )

        if all(key):
            positions.add(key)

    return positions


def generate_positions_for_material(material_key):
    """
    Helper function. Generates the matrices for different Biomaterial according to the freezer
    set-ups.

    Args:
        material_key (str): Biomaterial intended to store.

    Returns:
        positions (list): 
    Raises:
        ValueError: If input values are invalid #not yet but would be good
    """
    rules = STORAGE_RULES[material_key]
    positions = set()

    for freezer, rack in product(rules["freezers"], rules["racks"]):
        for box in map(str, range(1, rules["boxes_per_rack"] + 1)):
            for row, col in product(rules["rows"], rules["cols"]):
                pos = f"{row}{col}"
                positions.add((freezer, rack, box, pos))

    return positions


def get_available_positions(material_key, reference_rows):
    """
    GUI core Function. Generates the matrices for different Biomaterial according to the freezer
    set-ups. Calculates which positions are occupied and returns the sorted positions.

    Args:
        material_key (str): Biomaterial intended to store.
        reference_rows (List[Dict]): Existing REDCap data
 
    Returns:
        positions (list): Avaialbe positions for the selected Biomaterial.    
    """
    all_pos = generate_positions_for_material(material_key)
    occupied = get_occupied_positions(reference_rows)
    return sorted(all_pos - occupied)



def split_pos(pos):
    """
    Helper function. Splits the tube position in row and column such that the sorting algorithm
    is able to sort the positions after row and col sepperately. 

    Args:
        pos (list): Available positions
 
    Returns:
        row (str): Row position in box depends on matrix  
        col (int): Col position in box depends on matrix
    """
    row = pos[0]
    col = int(pos[1:])
    return row, col


def position_sort_key(item):
    """
    Helper function. Generates a sort key for Python inbuild sorted() function, such that the 
    freezer position is sorted via freezer, rack, box, pos for any particular Biofluid.

    Args:
        item: 
 
    Returns:
        positions (list): sorted positions       
    """
    freezer, rack, box, pos = item
    row, col = split_pos(pos)  #seperates it in for example A and 7 instead of A7, so that the sorting works 
    #print(type(col))
    return (
        FREEZER_ORDER.get(freezer, 99),
        int(rack),
        int(box),
        row,
        col,
    )

def pos_sort_key(pos):
    row = pos[0]
    col = int(pos[1:])
    return (row, col)


def save_positions_to_csv(path, positions):
    """
    Saves selected positions to CSV.

    Columns:
    freezer, rack, box, pos
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pos", "box", "rack", "freezer"])
        
        for freezer, rack, box, pos in positions:
            freezer_code = FREEZER_ORDER_BACK[freezer] #Umwandlung von 4deg -> 4 von nitrogen -> 5
            writer.writerow([pos, box, rack, freezer])

def select_positions_for_material(material, available_positions):
    """
    GUI core function. Selects available positions based on STORAGE_RULES for BIOFLUID, PAXGENE, DNA
    and CELLS. 

    Args:
        material (str): Biomaterial (must exist in STORAGE_RULES (Global var))
        available_positions (list): List of available positions

    Returns:
        list: Selected positions

    Raises:
        ValueError: If material has no storage rule
    """
    material = material.strip().upper()

    if material not in STORAGE_RULES:
        raise ValueError(
            f"Material '{material}' has no defined STORAGE_RULE."
        )

    # Biofluids get special selection logic; 15 at least in one box.
    if material == "BIOFLUID":
        return select_positions_biofluids(available_positions)

    # All others use single-position logic because it is more likely to have single aliquots
    return select_positions_single(material, available_positions)


    
def select_positions_single(material, available_positions, positionnumber = 20):
    """
    Helper function. Selects single positions (default 20) sequentially for PAXGENE, CELLS and DNA. 


    Args: 
        material (str): Biomaterial (must exist in STORAGE_RULES (Global var))
        available_positions (list): List of available positions
    Returns:
        list: Selected sorted positions    
    """
    return sorted(available_positions, key=position_sort_key)[:positionnumber]


def select_positions_biofluids(available_positions):
    """
    Helper function. Selects positions per box sequentially for BIOFLUIDS. 

    Args: 
        available_positions (list): List of available positions
    Returns:
        list: Selected sorted positions    
    """
    box_map = group_positions_by_box(available_positions)

    selected = []
    box_count = 0

    for (freezer, rack, box), positions in box_map.items():
        if len(positions) < 15:
            continue

        box_count += 1
        for pos in positions:
            selected.append((freezer, rack, box, pos))
            if len(selected) >= 40:
                return selected

        if box_count >= 2:
            break

    return selected


def group_positions_by_box(positions):
    """
    Helper function. Groups positions by (freezer, rack, box).
    args
        positions (list): List of available positions
    Returns:
        box_map: Dict[(freezer, rack, box), List[pos]]
    """
    box_map = defaultdict(list)

    for freezer, rack, box, pos in positions:
        box_map[(freezer, rack, box)].append(pos)

    # sort positions inside each box
    for key in box_map:
        box_map[key] = sorted(box_map[key], key=pos_sort_key)

    return box_map


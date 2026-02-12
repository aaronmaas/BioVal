#import libraries
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import tkinter.font as tkFont

from PIL import Image, ImageTk  # Pillow muss installiert sein: pip install pillow
import os
import sys
import subprocess
from config import API_URL, STORAGE_RULES, STUDY_ID_PATTERN
import utils as u
import positions as p
import validation as v
from redcap_api import download_reference_from_redcap

 
API_TOKEN = ""

#### you need to go through and change the functions - so that it works correctly less import

def open_file(path):
    if sys.platform.startswith("win"):
        os.startfile(path)              # Windows
    elif sys.platform == "darwin":
        subprocess.run(["open", path])  # macOS
    else:
        subprocess.run(["xdg-open", path])  # Linux
        
def ask_for_material(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("Select Biomaterial")
    dialog.geometry("300x150")
    dialog.grab_set()

    tk.Label(dialog, text="Select biomaterial:").pack(pady=10)

    material_var = tk.StringVar()
    combo = ttk.Combobox(
        dialog,
        textvariable=material_var,
        values=sorted(STORAGE_RULES.keys()),
        state="readonly"
    )
    combo.pack()
    combo.current(0)

    result = {"material": None}

    def confirm():
        result["material"] = material_var.get()
        dialog.destroy()

    ttk.Button(dialog, text="OK", command=confirm).pack(pady=10)

    dialog.wait_window()
    return result["material"]


def run_validation():
    try:
        # ===============================
        # 1. Download reference data
        # ===============================
        reference_rows = download_reference_from_redcap(API_URL, API_TOKEN)
        ref_path = "/home/aaron/Desktop/BioVal/data/Ref_file_test.csv" ###
        u.save_data_as_csv(reference_rows, ref_path)

        # ===============================
        # 2. NEW: Show available positions
        # ===============================
        material = ask_for_material(root)
        if not material:
            messagebox.showinfo("Cancelled", "No biomaterial selected.")
            return

        available_positions = p.get_available_positions(material, reference_rows)

        selected_positions = p.select_positions_for_material(material,available_positions)

        csv_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save Available Positions",
            initialfile=f"available_positions_{material}.csv"
        )
        #The GUI open directly the csv
        if csv_path:
            p.save_positions_to_csv(csv_path, selected_positions)
            open_file(csv_path)

        # ===============================
        # 3. Continue with import validation
        # ===============================
        import_path = filedialog.askopenfilename(title="Select Import CSV")
        _, import_rows = u.read_csv(import_path)

        v.validate_file(import_path, "Import file")
        v.validate_file(ref_path, "Reference data")

        v.check_internal_duplicates(import_rows, "Import file")
        v.check_internal_duplicates(reference_rows, "Reference data")

        occupied_pos = p.get_occupied_positions(reference_rows)
        duplicate_positions_count = v.check_duplicate_positions(import_rows, occupied_pos)

        import_rows, labid_messages = u.assign_lab_patient_ids(import_rows, reference_rows)
        u.save_data_as_csv(import_rows, import_path)

        # ===============================
        # 4. Report
        # ===============================
        report_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="Save Validation Report As"
        )

        if report_path:
            u.write_report(
                report_path,
                import_path,
                ref_path,
                labid_messages,
                import_rows,
                duplicate_positions_count
            )
            messagebox.showinfo("Success", "Validation completed!")
        else:
            messagebox.showinfo("Success", "Validation completed! No report saved.")

    except Exception as e:
        messagebox.showerror("Validation Error", str(e))

# --- GUI Setup ---
root = tk.Tk()
root.title("BioVal – Biorepository Validator")
root.geometry("700x520")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

# --- Optional Image ---
try:
    if getattr(sys, "frozen", False):
    	base_path = sys._MEIPASS
    else:
    	base_path = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(base_path,"images", "logo.jpeg")
    print("DEBUG logo path:", logo_path)
    print("DEBUG images dir exists:", os.path.exists(os.path.join(base_path, "images")))
    print("DEBUG logo exists:", os.path.exists(os.path.join(base_path, "images", "logo.jpeg")))
    print("DEBUG base_path contents:", os.listdir(base_path))

    img = Image.open(logo_path)

    #img = Image.open(os.path.join(base_path, "logo.jpeg"))
    img = img.resize((250, 250))
    photo = ImageTk.PhotoImage(img)
    logo_label = ttk.Label(main_frame, image=photo)
    logo_label.image = photo
    logo_label.pack(pady=(0, 10))
except Exception:
    print("No image found – skipping logo.")

# --- Welcome Text ---
# Define a custom font
custom_font = tkFont.Font( size=10)

#Label(root, text="I have default font-size").pack(pady=20)
#Label(root, text="I have a font-size of 25", font=custom_font).pack()


welcome = ttk.Label(
    main_frame,
    text=(
        "Welcome to BioVal!\n\n"
        "This tool helps you find available positions and validate biorepository REDCap import files.\n"
        "You’ll be prompted to select:\n"
        " - The Biomaterial you want to upload."
        " - A new import CSV file\n - the data you want to upload"
        " - A reference dataset for comparison - the data already stored in RedCap \n\n"
        "The tool checks patient IDs, sample positions, and generates a report."
    ),
    justify="center",
    wraplength=500,
    font = custom_font
)
welcome.pack(pady=10)

# --- Start Button ---
start_button = ttk.Button(main_frame, text="Start BioVal", command=run_validation)
start_button.pack(pady=20)

root.mainloop()

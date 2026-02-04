import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import itertools
import shutil
from gui_components.ui_utils import UIUtils

class SequentialRunManager:
    """
    Manages the Sequential/Batch Execution Window.
    
    Responsibilities:
    1. Identify variables available for sequencing.
    2. Generate Cartesian products of input variations.
    3. Manage the execution environment (folders, tape copying).
    4. Execute NJOY subprocesses.
    """

    def __init__(self, parent_app, active_modules):
        """
        :param parent_app: Reference to the main NJOYInputGUI (for access to paths/settings).
        :param active_modules: Reference to the list of currently active NJOY module objects.
        """
        self.root = parent_app.root
        self.parent = parent_app
        self.active_modules = active_modules
        
        # State containers
        self.seq_map = {}       # Maps display names to input objects
        self.defined_vars = []  # Stores user-defined sequences
        self.planned_runs = []  # Stores the generated job matrix

    def open_window(self):
        """Initializes and displays the Sequential Run Window."""
        if not self.active_modules:
            messagebox.showwarning("Project Empty", "Please add modules to the project first.")
            return

        self.win = tk.Toplevel(self.root)
        self.win.title("Sequential Input Generation & Runner")
        self.win.geometry("1000x750")

        # --- Layout Splitting ---
        # Left Pane: Variable Setup (Fixed Width)
        left_pane = tk.Frame(self.win, padx=10, pady=10, width=320)
        left_pane.pack(side="left", fill="y")
        left_pane.pack_propagate(False)

        # Right Pane: Table and Execution (Expandable)
        right_pane = tk.Frame(self.win, padx=10, pady=10)
        right_pane.pack(side="right", fill="both", expand=True)

        self._build_variable_definition_ui(left_pane)
        self._build_configuration_ui(right_pane)
        self._build_job_table_ui(right_pane)

    def _build_variable_definition_ui(self, parent):
        """Builds the Left Panel: Target selection and value input."""
        
        # --- Header with Help ---
        h_frame = tk.Frame(parent)
        h_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(h_frame, text="1. Define Variables", font=("Segoe UI", 11, "bold")).pack(side="left")
        
        def show_step1_help():
            desc = (
                "Select an active input field from the dropdown.\n"
                "Enter a list of values (space-separated) to iterate over.\n"
                "Click '+ Add Variable' to add it to the batch logic."
            )
            UIUtils.show_info(self.win, "Step 1: Define Variables", desc, "")
            
        tk.Button(h_frame, text="?", width=2, relief="flat", fg="blue", font=("Arial", 8, "bold"), 
                  command=show_step1_help).pack(side="left", padx=5)

        # 1. Populate Dropdown with Active Inputs
        tk.Label(parent, text="Select Active Input:", font=("Segoe UI", 9)).pack(anchor="w")
        
        combo_values = []
        self.seq_map = {}
        
        for m_idx, mod in enumerate(self.active_modules):
            for card in mod.cards:
                # Skip inactive cards
                if card.active_if is not None:
                    try: 
                        if not card.active_if(): continue
                    except: continue 
                
                for inp in card.inputs:
                    # Create a unique readable key
                    key = f"[{m_idx+1}] {mod.name.upper()} > {card.name} > {inp.name}"
                    self.seq_map[key] = (m_idx, card.name, inp.name, inp)
                    combo_values.append(key)

        self.target_var = tk.StringVar()
        self.cb_target = ttk.Combobox(parent, textvariable=self.target_var, values=combo_values, state="readonly")
        self.cb_target.pack(fill="x", pady=(0, 10))
        if combo_values: self.cb_target.current(0)

        # 2. Values Input Area
        tk.Label(parent, text="Values (Space separated):", font=("Segoe UI", 9)).pack(anchor="w")
        self.txt_seq = tk.Text(parent, height=5, font=("Consolas", 9), relief="groove", borderwidth=1)
        self.txt_seq.pack(fill="x", pady=(0, 2))

        # Helper: Add Files Button
        tk.Button(parent, text="🗂 Add Files", command=self._add_files_helper, bg="#e0e0e0", font=("Segoe UI", 8)).pack(anchor="e", pady=(0, 10))

        # 3. List of Added Variables
        tk.Label(parent, text="Variables to Vary:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lb_vars = tk.Listbox(parent, height=10, bg="#f0f0f0")
        self.lb_vars.pack(fill="both", expand=True, pady=(0, 5))

        # Action Buttons
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="Add Variable", command=self._add_variable_logic, bg="#e8f5e9").pack(side="left", fill="x", expand=True, padx=2)
        tk.Button(btn_frame, text="Remove Selected", command=self._remove_variable_logic, bg="#ffebee").pack(side="left", fill="x", expand=True, padx=2)

    def _build_configuration_ui(self, parent):
        """Builds Top-Right Panel: Paths and settings."""
        
        # --- Header with Help ---
        h_frame = tk.Frame(parent)
        h_frame.pack(fill="x")
        
        tk.Label(h_frame, text="2. Configuration", font=("Segoe UI", 11, "bold")).pack(side="left")
        
        def show_step2_help():
            desc = (
                "Output Directory: All run folders will be created here.\n"
                "NJOY Executable: Path to your installed NJOY executable."
            )
            UIUtils.show_info(self.win, "Step 2: Configuration", desc, "")
            
        tk.Button(h_frame, text="?", width=2, relief="flat", fg="blue", font=("Arial", 8, "bold"), 
                  command=show_step2_help).pack(side="left", padx=5)

        cfg_frame = tk.Frame(parent, bg="#f9f9f9", bd=1, relief="sunken", padx=10, pady=10)
        cfg_frame.pack(fill="x", pady=(5, 15))

        # Output Directory
        tk.Label(cfg_frame, text="Output Directory:", bg="#f9f9f9").grid(row=0, column=0, sticky="w")
        self.ent_outdir = tk.Entry(cfg_frame)
        self.ent_outdir.insert(0, self.parent.output_dir_path)
        self.ent_outdir.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Button(cfg_frame, text="...", width=3, command=lambda: self._browse_dir(self.ent_outdir)).grid(row=0, column=2)

        # Executable Path
        tk.Label(cfg_frame, text="NJOY Executable:", bg="#f9f9f9").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_exe = tk.Entry(cfg_frame)
        self.ent_exe.insert(0, self.parent.njoy_exe_path)
        self.ent_exe.grid(row=1, column=1, sticky="ew", padx=5)
        tk.Button(cfg_frame, text="...", width=3, command=lambda: self._browse_file(self.ent_exe)).grid(row=1, column=2)
        
        cfg_frame.columnconfigure(1, weight=1)

    def _build_job_table_ui(self, parent):
        """Builds Bottom-Right Panel: The Grid and Execution controls."""
        
        # --- Header with Help ---
        h_frame = tk.Frame(parent)
        h_frame.pack(fill="x")
        
        tk.Label(h_frame, text="3. Job List (Generated Combinations)", font=("Segoe UI", 11, "bold")).pack(side="left")
        
        def show_step3_help():
            desc = (
                "Click 'Generate Combinations' to create the full matrix of runs.\n"
                "Select specific rows and click 'Delete Selected' to remove unwanted cases.\n"
                "Click 'Execute Batch' to run all jobs in the list."
            )
            UIUtils.show_info(self.win, "Step 3: Job Matrix", desc, "")
            
        tk.Button(h_frame, text="?", width=2, relief="flat", fg="blue", font=("Arial", 8, "bold"), 
                  command=show_step3_help).pack(side="left", padx=5)

        # Table Controls
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill="x", pady=2)
        tk.Button(btn_frame, text="Generate Combinations", command=self._generate_table_logic, bg="#e3f2fd").pack(side="left", padx=2)
        tk.Button(btn_frame, text="Delete Selected Rows", command=self._delete_rows_logic, bg="#ffebee").pack(side="left", padx=2)

        # Treeview (Grid)
        cols = ("ID", "Parameters", "Output Folder")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="extended")
        self.tree.heading("ID", text="#")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("Parameters", text="Configuration")
        self.tree.column("Parameters", width=300)
        self.tree.heading("Output Folder", text="Folder Name")
        self.tree.column("Output Folder", width=200)
        
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="top", fill="both", expand=True)
        vsb.pack(side="right", fill="y", before=self.tree)

        # Launch Controls
        self.lbl_status = tk.Label(parent, text="Waiting...", fg="gray", font=("Segoe UI", 9))
        self.lbl_status.pack(pady=5)
        
        tk.Button(parent, text="🚀 EXECUTE BATCH", command=self._launch_jobs_logic, bg="#4caf50", fg="white", font=("Segoe UI", 11, "bold"), pady=10).pack(side="bottom", fill="x")

    # --- Logic Helpers ---

    def _add_files_helper(self):
        files = filedialog.askopenfilenames(title="Select Tapes for Sequence")
        if files:
            current = self.txt_seq.get("1.0", tk.END).strip()
            self.txt_seq.delete("1.0", tk.END)
            self.txt_seq.insert("1.0", (current + " " + " ".join(files)).strip())

    def _browse_dir(self, entry):
        d = filedialog.askdirectory()
        if d: 
            entry.delete(0, tk.END)
            entry.insert(0, d)

    def _browse_file(self, entry):
        f = filedialog.askopenfilename()
        if f:
            entry.delete(0, tk.END)
            entry.insert(0, f)

    def _add_variable_logic(self):
        display = self.target_var.get()
        raw_vals = self.txt_seq.get("1.0", tk.END).strip()
        
        if not display or not raw_vals:
            return
        
        # Clean splitting (handle newlines and commas)
        clean_vals = raw_vals.replace(",", " ").replace("\n", " ").split()
        if not clean_vals: return

        # Prevent duplicates
        for v in self.defined_vars:
            if v["display"] == display:
                messagebox.showwarning("Warning", "Variable already added.")
                return

        m_idx, c_name, i_name, inp_obj = self.seq_map[display]
        is_file_input = getattr(inp_obj, 'is_input_file', False)

        self.defined_vars.append({
            "display": display,
            "key": (m_idx, c_name, i_name),
            "values": clean_vals,
            "is_file_input": is_file_input,
            "base_unit": inp_obj.value if is_file_input else None
        })
        
        tag = "[FILE]" if is_file_input else "[VAL]"
        self.lb_vars.insert(tk.END, f"{tag} {display} ({len(clean_vals)})")
        self.txt_seq.delete("1.0", tk.END)

    def _remove_variable_logic(self):
        sel = self.lb_vars.curselection()
        if not sel: return
        idx = sel[0]
        self.lb_vars.delete(idx)
        self.defined_vars.pop(idx)

    def _generate_table_logic(self):
        # Clear table
        for row in self.tree.get_children(): self.tree.delete(row)
        self.planned_runs = []
        
        if not self.defined_vars: return

        # Cartesian Product Logic
        all_lists = [v["values"] for v in self.defined_vars]
        combinations = list(itertools.product(*all_lists))
        
        for i, combo in enumerate(combinations):
            folder_parts = [f"Run_{i+1}"]
            desc_parts = []
            run_config = []
            
            for j, val in enumerate(combo):
                var_def = self.defined_vars[j]
                var_name = var_def["display"].split(">")[-1].strip()
                
                # Sanitize filename
                safe_val = os.path.basename(str(val)).replace(".", "p")
                folder_parts.append(f"{var_name}_{safe_val}")
                
                # Description
                display_val = os.path.basename(val) if var_def["is_file_input"] else val
                desc_parts.append(f"{var_name}={display_val}")
                
                run_config.append({
                    "key": var_def["key"], 
                    "val": val, 
                    "is_file": var_def["is_file_input"],
                    "base_unit": var_def["base_unit"]
                })
            
            folder_name = "_".join(folder_parts)
            
            self.tree.insert("", "end", iid=str(i), values=(i+1, ", ".join(desc_parts), folder_name))
            
            self.planned_runs.append({
                "id": i+1,
                "folder": folder_name,
                "config": run_config
            })

    def _delete_rows_logic(self):
        selected = self.tree.selection()
        if not selected: return
        
        ids_to_remove = []
        for item in selected:
            vals = self.tree.item(item)['values']
            ids_to_remove.append(int(vals[0]))
            self.tree.delete(item)
            
        self.planned_runs = [r for r in self.planned_runs if r["id"] not in ids_to_remove]

    def _launch_jobs_logic(self):
        if not self.planned_runs:
            messagebox.showerror("Error", "Job list is empty.")
            return
        
        out_root = self.ent_outdir.get()
        exe = self.ent_exe.get()
        
        try: os.makedirs(out_root, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if not messagebox.askyesno("Confirm", f"Launch {len(self.planned_runs)} jobs?"): return

        # 1. SNAPSHOT CURRENT STATE (Backup)
        backup = self._create_state_backup()

        success = 0
        try:
            for run in self.planned_runs:
                self.lbl_status.config(text=f"Running Job {run['id']}...", fg="blue")
                self.win.update()

                # A. Apply Variables
                self._apply_run_config(run["config"])

                # B. Generate Input
                full_text = self._generate_full_input()

                # C. Setup Environment & Execute
                if self._execute_single_run(out_root, run["folder"], full_text, exe, run["config"]):
                    success += 1

            messagebox.showinfo("Done", f"Batch completed.\nSuccessful: {success}/{len(self.planned_runs)}")
            
            # Open Folder
            if os.name == 'nt': os.startfile(out_root)
            else: 
                try: subprocess.Popen(['xdg-open', out_root])
                except: pass

        except Exception as e:
            messagebox.showerror("Fatal Error", str(e))
        finally:
            # D. Restore Original State
            self._restore_state(backup)
            self.lbl_status.config(text="Idle", fg="black")

    # --- State Management Helpers ---

    def _create_state_backup(self):
        backup = []
        for mod in self.active_modules:
            m_state = {}
            for c in mod.cards:
                c_state = {}
                for inp in c.inputs: c_state[inp.name] = inp.value
                m_state[c.name] = c_state
            backup.append(m_state)
        return backup

    def _restore_state(self, backup):
        for i, mod in enumerate(self.active_modules):
            if i < len(backup):
                saved = backup[i]
                for c in mod.cards:
                    if c.name in saved:
                        for inp in c.inputs:
                            if inp.name in saved[c.name]:
                                inp.value = saved[c.name][inp.name]
                if hasattr(mod, 'regenerate'): mod.regenerate()
        
        # Refresh main GUI
        self.parent.update_preview()
        self.parent.reorder_modules_layout()

    def _apply_run_config(self, config):
        """Applies a specific run configuration to the active modules."""
        for cfg in config:
            m_idx, c_name, i_name = cfg["key"]
            val = cfg["val"]
            # Skip file inputs here (they are handled during file copy)
            if not cfg["is_file"]:
                if m_idx < len(self.active_modules):
                    mod = self.active_modules[m_idx]
                    for c in mod.cards:
                        if c.name == c_name:
                            for inp in c.inputs:
                                if inp.name == i_name:
                                    inp.value = val
                    if hasattr(mod, 'regenerate'): mod.regenerate()

    def _generate_full_input(self):
        full_text = ""
        for mod in self.active_modules:
            full_text += mod.write() + "\n"
        full_text += "stop\n"
        return full_text

    def _execute_single_run(self, root, folder, content, exe, config):
        job_dir = os.path.join(root, folder)
        os.makedirs(job_dir, exist_ok=True)

        # 1. Copy Environment Tapes (Dependencies)
        for unit, path in self.parent.user_tapes.items():
            if os.path.exists(path):
                try: shutil.copy(path, os.path.join(job_dir, f"tape{unit}"))
                except: pass

        # 2. Copy Variable File Inputs (if any)
        for cfg in config:
            if cfg["is_file"] and os.path.exists(cfg["val"]):
                dest = os.path.join(job_dir, f"tape{cfg['base_unit']}")
                try: shutil.copy(cfg["val"], dest)
                except Exception as e: print(f"Copy error: {e}")

        # 3. Write Input
        with open(os.path.join(job_dir, "input.inp"), "w") as f: f.write(content)

        # 4. Run
        try:
            with open(os.path.join(job_dir, "output.out"), "w") as fout:
                subprocess.run([exe], input=content.encode('utf-8'), stdout=fout, stderr=subprocess.STDOUT, cwd=job_dir, check=True)
            return True
        except Exception as e:
            print(f"Execution failed: {e}")
            return False
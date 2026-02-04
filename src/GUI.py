from modules.acer import Acer
from modules.moder import Moder
from modules.reconr import Reconr
from modules.broadr import Broadr
from modules.thermr import Thermr       
from modules.groupr import Groupr
from modules.viewr import Viewr
from modules.errorr import Errorr
from modules.plotr import Plotr
from modules.unresr import Unresr
from modules.heatr import Heatr


from class_def import NjoyCard, NjoyInput
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from gui_components.GUI_helper import CollapsibleFrame
import Data_bases 
import os
import shutil
import subprocess

# Registry of Modules
AVAILABLE_MODULES = {
    "MODER": Moder,
    "RECONR": Reconr, #  <-- Add future classes here
    "BROADR": Broadr,
    "THERMR": Thermr,
    "ACER": Acer,
    "GROUPR": Groupr,
    "VIEWR": Viewr,
    "ERRORR": Errorr,   
    "PLOTR": Plotr,
    "UNRESR": Unresr,
    "HEATR": Heatr,
    # ...
}

# --- NEW IMPORTS FOR PDF VIEWING ---


#==============================================================================
# 2. MAIN GUI APPLICATION
# ==============================================================================

class NJOYInputGUI:
    def __init__(self, root):
        self.root = root
        self.active_modules = [] 
        
        # --- Data Storage ---
        self.njoy_exe_path = ""
        self.output_dir_path = os.path.join(os.getcwd(), "njoy_run")
        self.user_tapes = {}     
        self.module_tapes = {}   

        self._setup_view()
        self._bind_global_events()

    def _setup_view(self):
        self.root.title("NJOY Input Builder & Launcher")
        # CHANGED: Bigger window
        self.root.geometry("1400x900") 
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # --- Top Toolbar ---
        top_frame = tk.Frame(self.root, pady=5, padx=5, bg="#f0f0f0")
        top_frame.grid(row=0, column=0, sticky="ew")

        tk.Label(top_frame, text="Select Module:", bg="#f0f0f0").pack(side="left")
        self.module_var = tk.StringVar()
        self.mod_dropdown = ttk.Combobox(top_frame, textvariable=self.module_var, values=list(AVAILABLE_MODULES.keys()), state="readonly")
        if AVAILABLE_MODULES: self.mod_dropdown.current(0)
        self.mod_dropdown.pack(side="left", padx=5)

        tk.Button(top_frame, text="Add Module", command=self.add_module, bg="#e6f2ff").pack(side="left", padx=5)
        tk.Button(top_frame, text="Update Preview", command=self.update_preview).pack(side="left", padx=5)
        tk.Button(top_frame, text="Export .inp", command=self.export_file, bg="#ccffcc").pack(side="right", padx=5)

        # --- Main Split Area ---
        paned = ttk.PanedWindow(self.root, orient='horizontal')
        paned.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # 1. LEFT: Input Deck Builder
        left_container = tk.Frame(paned)
        paned.add(left_container, weight=3) 
        self.canvas = tk.Canvas(left_container, bg="white")
        scrollbar = tk.Scrollbar(left_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        # 2. RIGHT: Split into 3 Vertical Sections
        right_container = tk.Frame(paned)
        paned.add(right_container, weight=3)
        
        right_paned = ttk.PanedWindow(right_container, orient='vertical')
        right_paned.pack(fill="both", expand=True)

        # --- RIGHT TOP: Preview ---
        preview_frame = tk.LabelFrame(right_paned, text="1. Input File Preview", padx=5, pady=5)
        right_paned.add(preview_frame, weight=2)
        self.preview_text = tk.Text(preview_frame, wrap="none", font=("Courier", 10), bg="#f5f5f5")
        preview_scroll = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        self.preview_text.pack(side="left", fill="both", expand=True)
        preview_scroll.pack(side="right", fill="y")

        # --- RIGHT MIDDLE: Tape Library (Split Columns) ---
        library_frame = tk.LabelFrame(right_paned, text="2. Tape Library", padx=5, pady=5)
        right_paned.add(library_frame, weight=2)
        
        # Library Toolbar
        lib_tool = tk.Frame(library_frame)
        lib_tool.pack(fill="x", pady=(0, 5))
        tk.Button(lib_tool, text="+ Load Input File", command=self.add_input_tape, bg="#ddffdd").pack(side="left")
        tk.Label(lib_tool, text="", fg="gray").pack(side="left", padx=5)

        # Two Columns Area
        lib_split = tk.Frame(library_frame)
        lib_split.pack(fill="both", expand=True)
        lib_split.columnconfigure(0, weight=1)
        lib_split.columnconfigure(1, weight=1)

        # Col 1: User Inputs
        tk.Label(lib_split, text="User Loaded Inputs", fg="green", font=("bold")).grid(row=0, column=0, sticky="w")
        self.tree_user = ttk.Treeview(lib_split, columns=("Unit", "File"), show='headings', height=6)
        self.tree_user.heading("Unit", text="Unit")
        self.tree_user.heading("File", text="File Name")
        self.tree_user.column("Unit", width=40, anchor="center")
        self.tree_user.grid(row=1, column=0, sticky="nsew", padx=(0,5))

        self.tree_user.bind("<Button-3>", self._show_user_lib_menu) # Windows/Linux
        if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
            self.tree_user.bind("<Button-2>", self._show_user_lib_menu) # MacOS
        
        # Col 2: Module Outputs
        tk.Label(lib_split, text="Module Outputs", fg="blue", font=("bold")).grid(row=0, column=1, sticky="w")
        self.tree_mods = ttk.Treeview(lib_split, columns=("Unit", "Desc"), show='headings', height=6)
        self.tree_mods.heading("Unit", text="Unit")
        self.tree_mods.heading("Desc", text="Generated By")
        self.tree_mods.column("Unit", width=40, anchor="center")
        self.tree_mods.grid(row=1, column=1, sticky="nsew")

        # --- RIGHT BOTTOM: Job Manager ---
        launch_frame = tk.LabelFrame(right_paned, text="3. Execution Manager", padx=5, pady=5, bg="#eeeeee")
        right_paned.add(launch_frame, weight=1)

        # NJOY Executable
        exe_row = tk.Frame(launch_frame, bg="#eeeeee")
        exe_row.pack(fill="x", pady=2)
        tk.Label(exe_row, text="NJOY Exe:", width=10, anchor="w", bg="#eeeeee").pack(side="left")
        self.ent_exe = tk.Entry(exe_row)
        self.ent_exe.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(exe_row, text="Browse...", command=self.browse_exe).pack(side="right")

        # Output Folder
        dir_row = tk.Frame(launch_frame, bg="#eeeeee")
        dir_row.pack(fill="x", pady=2)
        tk.Label(dir_row, text="Output Dir:", width=10, anchor="w", bg="#eeeeee").pack(side="left")
        self.ent_dir = tk.Entry(dir_row)
        self.ent_dir.insert(0, self.output_dir_path)
        self.ent_dir.pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(dir_row, text="Browse...", command=self.browse_output_dir).pack(side="right")

        # Launch Button
        tk.Button(launch_frame, text="🚀 LAUNCH NJOY", command=self.run_njoy, bg="orange", fg="white", font=("Arial", 14, "bold"), height=2).pack(fill="x", pady=10)

    def _bind_global_events(self):
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # ==========================================================================
    #  PART 3: TAPE LIBRARY LOGIC (SEPARATE)
    # ==========================================================================
    def add_input_tape(self):
        """User loads a file and assigns a unit number."""
        f = filedialog.askopenfilename(title="Select Input ENDF/PENDF Tape")
        if not f: return
        
        # Ask for unit number
        default_unit = 20
        while default_unit in self.user_tapes: default_unit += 1
        
        unit = simpledialog.askinteger("Assign Unit", f"Assign NJOY Unit Number for:\n{os.path.basename(f)}", 
                                       initialvalue=default_unit, minvalue=20, maxvalue=99)
        if unit:
            if unit in self.user_tapes:
                if not messagebox.askyesno("Overwrite", f"Unit {unit} is already in use. Overwrite?"):
                    return
            self.user_tapes[unit] = f
            self.refresh_library()

    def refresh_library(self):
        """Clears and repopulates the library trees."""
        # 1. Update User Tapes (Left Column)
        for item in self.tree_user.get_children(): self.tree_user.delete(item)
        
        for unit, path in sorted(self.user_tapes.items()):
            filename = os.path.basename(path)
            self.tree_user.insert("", "end", values=(unit, filename))

        # 2. Update Module Outputs (Right Column)
        for item in self.tree_mods.get_children(): self.tree_mods.delete(item)
        
        for unit, desc in sorted(self.module_tapes.items()):
            self.tree_mods.insert("", "end", values=(unit, desc))


    # ==========================================================================
    #  NEW LIBRARY FEATURES
    # ==========================================================================
    def _show_user_lib_menu(self, event):
        """Displays context menu on right-click."""
        # Identify row under mouse
        item = self.tree_user.identify_row(event.y)
        if not item: return
        
        # Select it
        self.tree_user.selection_set(item)
        
        # Create Menu
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Change Unit Number", command=self.change_tape_unit)
        menu.add_separator()
        menu.add_command(label="Remove File", command=self.remove_input_tape, foreground="red")
        
        # Show Menu
        menu.post(event.x_root, event.y_root)

    def remove_input_tape(self):
        """Deletes the selected tape from the user library."""
        selected = self.tree_user.selection()
        if not selected: return
        
        # Get Unit from tree values
        item_vals = self.tree_user.item(selected[0], "values")
        unit = int(item_vals[0])
        
        if messagebox.askyesno("Confirm Remove", f"Remove Tape {unit} from library?"):
            if unit in self.user_tapes:
                del self.user_tapes[unit]
                self.refresh_library()

    def change_tape_unit(self):
        """Changes the key (unit number) in the dictionary."""
        selected = self.tree_user.selection()
        if not selected: return
        
        item_vals = self.tree_user.item(selected[0], "values")
        old_unit = int(item_vals[0])
        path = self.user_tapes[old_unit]
        
        new_unit = simpledialog.askinteger("Change Unit", f"Enter new unit number for:\n{os.path.basename(path)}", 
                                           initialvalue=old_unit, minvalue=20, maxvalue=99)
        
        if new_unit and new_unit != old_unit:
            # Check collision
            if new_unit in self.user_tapes:
                if not messagebox.askyesno("Overwrite", f"Unit {new_unit} is already in use by another file.\nOverwrite it?"):
                    return
            
            # Perform Swap
            del self.user_tapes[old_unit]
            self.user_tapes[new_unit] = path
            self.refresh_library()

    # ==========================================================================
    #  PART 4: NJOY EXECUTION LOGIC (SEPARATE)
    # ==========================================================================
    def browse_exe(self):
        f = filedialog.askopenfilename(title="Locate NJOY Executable")
        if f:
            self.njoy_exe_path = f
            self.ent_exe.delete(0, tk.END)
            self.ent_exe.insert(0, f)

    def browse_output_dir(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            self.output_dir_path = d
            self.ent_dir.delete(0, tk.END)
            self.ent_dir.insert(0, d)

    def run_njoy(self):
        # 1. Verify Configuration
        exe = self.ent_exe.get()
        if not exe or not os.path.exists(exe):
            messagebox.showerror("Error", "Invalid NJOY Executable path.")
            return

        out_dir = self.ent_dir.get()
        if not out_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return
        
        # 2. Create Output Directory
        if not os.path.exists(out_dir):
            try:
                os.makedirs(out_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create directory:\n{e}")
                return

        # 3. Write 'input.inp'
        inp_content = self.preview_text.get("1.0", tk.END)
        inp_path = os.path.join(out_dir, "input.inp")
        try:
            with open(inp_path, "w") as f:
                f.write(inp_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write input file:\n{e}")
            return

        # 4. Copy User Tapes (Input Files)
        for unit, src_path in self.user_tapes.items():
            dst_name = f"tape{unit}"
            dst_path = os.path.join(out_dir, dst_name)
            try:
                if os.path.exists(dst_path): os.remove(dst_path)
                shutil.copy(src_path, dst_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy tape {unit}:\n{e}")
                return

        # 5. Execute NJOY
        cmd = [exe]
        output_file_path = os.path.join(out_dir, "output") # Standard NJOY output file

        try:
            with open(inp_path, "r") as stdin_f:
                # Capture standard streams
                proc = subprocess.run(cmd, stdin=stdin_f, cwd=out_dir, capture_output=True, text=True)
            
            # Save Console Log (stdout)
            with open(os.path.join(out_dir, "output.log"), "w") as log:
                log.write(proc.stdout)
            
            # Save Error Log (stderr) if exists
            if proc.stderr:
                with open(os.path.join(out_dir, "error.log"), "w") as err:
                    err.write(proc.stderr)

            # 6. CHECK FOR ERRORS
            if proc.returncode == 0:
                messagebox.showinfo("Success", f"NJOY Run Complete!\nFiles are in: {out_dir}")
            else:
                # Header
                error_msg = f"NJOY Execution Failed (Error Code {proc.returncode})\n\n"
                
                # DISPLAY OUTPUT CONTENT (What would be in output.txt)
                # We take the last 50 lines to ensure the message box fits on screen.
                if proc.stdout:
                    lines = proc.stdout.splitlines()
                    tail_content = "\n".join(lines[-50:]) 
                    error_msg += f"--- NJOY OUTPUT (Last 50 lines) ---\n{tail_content}\n"
                else:
                    error_msg += "(No NJOY output produced)\n"

                # Add System Errors (like segmentation faults) if they exist
                if proc.stderr:
                    error_msg += f"\n--- SYSTEM ERROR (STDERR) ---\n{proc.stderr}\n"

                messagebox.showerror("Execution Error", error_msg)

        except Exception as e:
            messagebox.showerror("Execution Error", str(e))

    # ==========================================================================
    #  PART 5: MODULE MANAGEMENT (UPDATED WITH SWAP)
    # ==========================================================================
    def add_module(self):
        mod_name = self.module_var.get()
        if mod_name not in AVAILABLE_MODULES: return

        mod_class = AVAILABLE_MODULES[mod_name]
        module_instance = mod_class()
        self.active_modules.append(module_instance)

        # Instead of just building one, we refresh the whole view to ensure order
        self.refresh_modules_view()
        self.update_preview()

    def refresh_modules_view(self):
        """Clears the scroll frame and rebuilds all modules in the current order."""
        # 1. Clear existing widgets in the scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # 2. Rebuild widgets for every module in the list
        for mod in self.active_modules:
            self._build_module_widgets(mod)

    def move_module_up(self, module):
        """Swaps the module with the one above it."""
        idx = self.active_modules.index(module)
        if idx > 0: # Can't move up if it's first
            self.active_modules[idx], self.active_modules[idx-1] = self.active_modules[idx-1], self.active_modules[idx]
            self.refresh_modules_view()
            self.update_preview()

    def move_module_down(self, module):
        """Swaps the module with the one below it."""
        idx = self.active_modules.index(module)
        if idx < len(self.active_modules) - 1: # Can't move down if it's last
            self.active_modules[idx], self.active_modules[idx+1] = self.active_modules[idx+1], self.active_modules[idx]
            self.refresh_modules_view()
            self.update_preview()

    def _build_module_widgets(self, module):
        def show_mod_help():
            ref = getattr(module, 'ref', "N/A")
            self.show_info(module.name.upper(), module.description, ref)

        # 1. Module Container
        container = CollapsibleFrame(self.scroll_frame, title=f"{module.name.upper()}", help_command=show_mod_help, show_delete=True)
        container.pack(fill="x", padx=5, pady=5)

        # --- NEW: ADD ARROW BUTTONS TO HEADER ---
        # We access container.title_frame directly to add buttons
        btn_frame = tk.Frame(container.title_frame, bg="#e1e1e1")
        btn_frame.pack(side="right", padx=5)

        # Up Button
        tk.Button(btn_frame, text="▲", width=2, relief="flat", bg="#e1e1e1", 
                  command=lambda: self.move_module_up(module)).pack(side="left", padx=1)
        
        # Down Button
        tk.Button(btn_frame, text="▼", width=2, relief="flat", bg="#e1e1e1", 
                  command=lambda: self.move_module_down(module)).pack(side="left", padx=1)
        # ----------------------------------------

        # Delete Logic
        def delete_logic():
            if module in self.active_modules: self.active_modules.remove(module)
            # Instead of destroying container, we refresh to keep indices clean
            self.refresh_modules_view()
            self.update_preview()
        container.del_btn.configure(command=delete_logic)

        # Build Card Widgets (Same as before)
        card_frames = []
        for card in module.cards:
            def show_card_help(c=card):
                self.show_info(f"Card: {c.name}", c.description, c.ref)
            
            card_container = CollapsibleFrame(container.sub_frame, title=card.name, help_command=show_card_help, show_delete=False)
            
            for inp in card.inputs:
                self._build_input_row(card_container.sub_frame, inp, module, card_frames)
            
            card_frames.append((card, card_container))

        self._check_visibility_rules(card_frames)

    def _build_input_row(self, parent, inp_obj, module, card_frames):
        row = tk.Frame(parent)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=inp_obj.name, width=15, anchor="w").pack(side="left")
        
        var = tk.StringVar(value=str(inp_obj.value))
        entry = tk.Entry(row, textvariable=var)
        entry.pack(side="left", fill="x", expand=True) 

        if inp_obj.options:
            def open_list():
                self.open_selection_list(inp_obj, var, inp_obj.options)
            tk.Button(row, text="≡", width=2, command=open_list, bg="#e0e0e0").pack(side="left", padx=(0, 2))

        dot = tk.Label(row, text="●", fg="green")
        dot.pack(side="left", padx=5)

        def show_inp_help():
            self.show_info(f"Input: {inp_obj.name}", inp_obj.description, inp_obj.ref)
        tk.Button(row, text="?", width=2, command=show_inp_help, relief="flat", fg="blue").pack(side="left")

        def on_change(*args):
            inp_obj.value = var.get()
            if inp_obj.validate():
                entry.config(bg="white")
                dot.config(fg="green")
            else:
                entry.config(bg="#ffdddd")
                dot.config(fg="red")
            self._check_visibility_rules(card_frames)
            self.update_preview()

        var.trace_add("write", on_change)

    def _check_visibility_rules(self, card_frames):
        for card, frame in card_frames:
            visible = True
            if card.active_if is not None:
                visible = card.active_if()
            if visible: frame.pack(fill="x", pady=5)
            else: frame.pack_forget()

    def update_preview(self):
        full_text = ""
        self.module_tapes = {} 

        for mod in self.active_modules:
            full_text += mod.write() + "\n"
            for out_unit in mod.output_files:
                try:
                    u = int(out_unit)
                    self.module_tapes[u] = f"Output of {mod.name.upper()}"
                except: pass
        full_text += "stop\n"

        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert(tk.END, full_text)
        self.preview_text.config(state="disabled")
        self.refresh_library()

    def show_info(self, title, description, ref):
        top = tk.Toplevel(self.root)
        top.title(f"Help: {title}")
        top.geometry("500x300") # Slightly larger default
        
        # Make window resizable
        top.columnconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)

        # Title
        tk.Label(top, text=title, font=("Arial", 12, "bold"), pady=10).grid(row=0, column=0, sticky="ew")
        
        # Content Frame
        f = tk.Frame(top, padx=10, pady=5)
        f.grid(row=1, column=0, sticky="nsew")
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1) # Text area expands
        
        # CHANGED: Use Text widget instead of Label for automatic resizing/wrapping
        txt = tk.Text(f, wrap="word", font=("Arial", 10), bg="#f0f0f0", relief="flat", padx=5, pady=5)
        txt.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar (just in case)
        scroll = tk.Scrollbar(f, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=scroll.set)
        scroll.grid(row=0, column=1, sticky="ns")
        
        # Insert Text
        full_text = f"DESCRIPTION:\n{description or 'N/A'}\n\nREFERENCE:\n{ref or 'N/A'}"
        txt.insert("1.0", full_text)
        
        # Add bold tags for headers
        txt.tag_config("bold", font=("Arial", 10, "bold"))
        txt.tag_add("bold", "1.0", "1.12") # "DESCRIPTION:"
        
        # Find position of REFERENCE label to bold it
        ref_idx = txt.search("REFERENCE:", "1.0", stopindex=tk.END)
        if ref_idx:
            end_idx = f"{ref_idx} + 10 chars"
            txt.tag_add("bold", ref_idx, end_idx)
            
        txt.config(state="disabled") # Make read-only

        # Close Button
        tk.Button(top, text="Close", command=top.destroy).grid(row=2, column=0, pady=10)
    def open_selection_list(self, inp_obj, tk_var, options_dict):
        top = tk.Toplevel(self.root)
        top.title(f"Select {inp_obj.name}")
        top.geometry("400x400")
        search_frame = tk.Frame(top, padx=5, pady=5)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="Filter:").pack(side="left")
        search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=search_var).pack(side="left", fill="x", expand=True)
        lb = tk.Listbox(top, height=15)
        lb.pack(fill="both", expand=True, padx=5)
        all_items = [f"{k} : {v}" for k, v in options_dict.items()]
        def pop(filt=""):
            lb.delete(0, tk.END)
            for i in all_items: 
                if filt.lower() in i.lower(): lb.insert(tk.END, i)
        pop()
        search_var.trace_add("write", lambda *a: pop(search_var.get()))
        def sel(e=None):
            if lb.curselection():
                tk_var.set(lb.get(lb.curselection()[0]).split(" : ")[0])
                top.destroy()
        lb.bind("<Double-Button-1>", sel)
        tk.Button(top, text="Select", command=sel, bg="#ddffdd").pack(fill="x")

    def export_file(self):
        text = self.preview_text.get("1.0", tk.END)
        path = filedialog.asksaveasfilename(defaultextension=".inp", filetypes=[("NJOY Input", "*.inp")])
        if path:
            with open(path, "w") as f: f.write(text)
            messagebox.showinfo("Success", f"Saved to {path}")


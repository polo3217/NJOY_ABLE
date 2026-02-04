# Import Modules
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
from modules.purr import Purr
from modules.gaspr import Gaspr

# Import UI Components
from gui_components.execution_panel import ExecutionPanel
from gui_components.library_panel import TapeLibraryPanel
from gui_components.GUI_helper import CollapsibleFrame, SmartInputRow

# Import New Managers
from gui_components.project_manager import ProjectManager
from gui_components.sequential_runner import SequentialRunManager
from gui_components.ui_utils import UIUtils

import tkinter as tk
from tkinter import ttk, messagebox
import os

AVAILABLE_MODULES = {
    "MODER": Moder, "RECONR": Reconr, "BROADR": Broadr, "THERMR": Thermr,
    "ACER": Acer, "GROUPR": Groupr, "VIEWR": Viewr, "ERRORR": Errorr,   
    "PLOTR": Plotr, "UNRESR": Unresr, "HEATR": Heatr, "PURR": Purr, "GASPR": Gaspr
}

class NJOYInputGUI:
    def __init__(self, root):
        self.root = root
        self.active_modules = [] 
        
        self.njoy_exe_path = "njoy21"
        self.output_dir_path = os.path.join(os.getcwd(), "njoy_seq_runs")
        self.user_tapes = {}     
        self.module_tapes = {}   

        # Initialize Helper Classes
        self.project_manager = ProjectManager(self, AVAILABLE_MODULES)
        self.seq_runner = SequentialRunManager(self, self.active_modules)

        self._setup_view()

    def _setup_view(self):
        self.root.title("NJOY_Able")
        self.root.geometry("1400x900") 
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Style Config
        style = ttk.Style()
        style.theme_use('clam')
        SMALL_FONT = ("Segoe UI", 8)
        BOLD_FONT = ("Segoe UI", 8, "bold")
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white", font=SMALL_FONT)
        style.configure("TButton", font=SMALL_FONT)
        self.root.configure(bg="white")

        # --- TOOLBAR ---
        top = tk.Frame(self.root, pady=2, padx=5, bg="#f0f0f0")
        top.grid(row=0, column=0, sticky="ew")

        # Module Selection
        tk.Label(top, text="Select Module:", bg="#f0f0f0", font=SMALL_FONT).pack(side="left")
        self.module_var = tk.StringVar()
        self.cb_mod = ttk.Combobox(top, textvariable=self.module_var, values=list(AVAILABLE_MODULES.keys()), state="readonly", width=15)
        if AVAILABLE_MODULES: self.cb_mod.current(0)
        self.cb_mod.pack(side="left", padx=5)

        ttk.Button(top, text="Add", command=self.add_module, width=6).pack(side="left", padx=2)
        ttk.Button(top, text="Preview", command=self.update_preview, width=8).pack(side="left", padx=2)
        
        # --- Top Toolbar ---
        # ... (Module selector, Add, Preview buttons) ...
        
        # Save / Load
        tk.Frame(top, width=20, bg="#f0f0f0").pack(side="left")
        tk.Button(top, text="💾 Save Project", command=self.project_manager.save_project, bg="#e0f7fa", relief="flat", font=SMALL_FONT).pack(side="left", padx=2)
        tk.Button(top, text="📂 Load Project", command=self.project_manager.load_project, bg="#fff9c4", relief="flat", font=SMALL_FONT).pack(side="left", padx=2)
        
        def show_sl_help():
            UIUtils.show_info(self.root, "Project Management", "Save/Load allows you to persist the entire state of the GUI.", "")
        tk.Button(top, text="?", width=2, relief="flat", fg="blue", bg="#f0f0f0", font=("Arial", 9, "bold"), command=show_sl_help).pack(side="left", padx=2)

        # Sequential Run
        tk.Frame(top, width=20, bg="#f0f0f0").pack(side="left")
        tk.Button(top, text="⚡ Sequential Run", command=self.seq_runner.open_window, bg="#ffccbc", relief="flat", font=BOLD_FONT).pack(side="left", padx=2)

        # --- NEW: Help Button for Sequential Run ---
        def show_seq_help():
            desc = (
                "SEQUENTIAL RUNNER:\n"
                "Perform parametric sweeps or batch jobs.\n"
                "1. Select a variable (e.g. Temperature) or Input Tape.\n"
                "2. Define values.\n"
                "3. Generate and run combinations."
            )
            UIUtils.show_info(self.root, "Sequential Runner", desc, "")
        tk.Button(top, text="?", width=2, relief="flat", fg="blue", bg="#f0f0f0", font=("Arial", 9, "bold"), command=show_seq_help).pack(side="left", padx=2)
        # ------------------------------------------

        tk.Button(top, text="Export .inp", command=self.export_file, bg="#ccffcc", relief="flat", font=SMALL_FONT).pack(side="right", padx=5)

        

        # --- MAIN AREA ---
        paned = ttk.PanedWindow(self.root, orient='horizontal')
        paned.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        # Left: Builder
        left_cont = ttk.Frame(paned)
        paned.add(left_cont, weight=3) 
        self.canvas = tk.Canvas(left_cont, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_cont, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = ttk.Frame(self.canvas)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # Right: Panels
        right_container = ttk.Frame(paned)
        paned.add(right_container, weight=3)
        right_paned = ttk.PanedWindow(right_container, orient='vertical')
        right_paned.pack(fill="both", expand=True)

        # Preview
        preview_frame = tk.LabelFrame(right_paned, text="1. Preview", padx=2, pady=2, bg="white", font=BOLD_FONT)
        right_paned.add(preview_frame, weight=2)
        self.preview_text = tk.Text(preview_frame, wrap="none", font=("Consolas", 11), bg="#f5f5f5", relief="flat")
        preview_scroll = ttk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scroll.set)
        self.preview_text.pack(side="left", fill="both", expand=True)
        preview_scroll.pack(side="right", fill="y")

        # Panels
        self.lib_panel = TapeLibraryPanel(right_paned, controller=self)
        right_paned.add(self.lib_panel, weight=2) 
        self.exec_panel = ExecutionPanel(right_paned, controller=self)
        right_paned.add(self.exec_panel, weight=1)

    # --- LOGIC ---
    def add_module(self):
        mod_name = self.module_var.get()
        if mod_name not in AVAILABLE_MODULES: return
        new_mod = AVAILABLE_MODULES[mod_name]()
        new_mod.cached_widget = self._create_module_widget(new_mod)
        self.active_modules.append(new_mod)
        self.reorder_modules_layout()
        self.update_preview()

    def reorder_modules_layout(self):
        for child in self.scroll_frame.winfo_children(): child.pack_forget()
        for mod in self.active_modules:
            if hasattr(mod, 'cached_widget'): mod.cached_widget.pack(fill="x", padx=2, pady=2)
        self.scroll_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def move_module_up(self, module):
        idx = self.active_modules.index(module)
        if idx > 0:
            self.active_modules[idx], self.active_modules[idx-1] = self.active_modules[idx-1], self.active_modules[idx]
            self.reorder_modules_layout()
            self.update_preview()

    def move_module_down(self, module):
        idx = self.active_modules.index(module)
        if idx < len(self.active_modules) - 1:
            self.active_modules[idx], self.active_modules[idx+1] = self.active_modules[idx+1], self.active_modules[idx]
            self.reorder_modules_layout()
            self.update_preview()

    def delete_module(self, module):
        if module in self.active_modules:
            if hasattr(module, 'cached_widget'): module.cached_widget.destroy()
            self.active_modules.remove(module)
            self.reorder_modules_layout()
            self.update_preview()

    def _create_module_widget(self, module):
        def show_mod_help():
            ref = getattr(module, 'ref', "N/A")
            UIUtils.show_info(self.root, module.name.upper(), module.description, ref)

        container = CollapsibleFrame(self.scroll_frame, title=f"{module.name.upper()}", help_command=show_mod_help, show_delete=True)
        
        btn_frame = tk.Frame(container.title_frame, bg="#e1e1e1")
        btn_frame.pack(side="right", padx=2)
        tk.Button(btn_frame, text="▲", width=2, relief="flat", bg="#e1e1e1", font=("Arial", 7), pady=0, command=lambda: self.move_module_up(module)).pack(side="left", padx=0)
        tk.Button(btn_frame, text="▼", width=2, relief="flat", bg="#e1e1e1", font=("Arial", 7), pady=0, command=lambda: self.move_module_down(module)).pack(side="left", padx=0)
        container.del_btn.configure(command=lambda: self.delete_module(module))

        card_frames = []
        for card in module.cards:
            def show_card_help(c=card): UIUtils.show_info(self.root, f"Card: {c.name}", c.description, c.ref)
            card_cont = CollapsibleFrame(container.sub_frame, title=card.name, help_command=show_card_help, show_delete=False)
            
            for inp in card.inputs:
                row = SmartInputRow(
                    parent=card_cont.sub_frame,
                    inp_obj=inp,
                    update_callback=lambda: [self._check_visibility_rules(card_frames), self.update_preview()],
                    options_callback=lambda obj, var, opts: UIUtils.open_selection_list(self.root, obj, var, opts),
                    help_callback=lambda t, d, r: UIUtils.show_info(self.root, t, d, r)
                )
                row.pack(fill="x")
            
            card_frames.append((card, card_cont))
        
        self._check_visibility_rules(card_frames)
        return container

    def _check_visibility_rules(self, card_frames):
        desired_visible = []
        for card, frame in card_frames:
            if card.active_if is None or card.active_if(): desired_visible.append(frame)
        
        current_visible = [f for c, f in card_frames if f.winfo_manager() != '']
        if desired_visible == current_visible: return

        for card, frame in card_frames: frame.pack_forget()
        for frame in desired_visible: frame.pack(fill="x", pady=2)

    def update_preview(self):
        current_yview = self.preview_text.yview()
        full_text = ""
        self.module_tapes = {} 
        try:
            for mod in self.active_modules:
                try:
                    full_text += mod.write() + "\n"
                    for out_unit in mod.output_files:
                        try: self.module_tapes[int(out_unit)] = f"Output of {mod.name.upper()}"
                        except: pass
                except Exception:
                    full_text += f"!!! Error generating {mod.name.upper()} !!!\n"
            
            full_text += "stop\n"
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, full_text)
            self.preview_text.yview_moveto(current_yview[0])
            self.preview_text.config(state="disabled")
            self.lib_panel.refresh()
        except Exception as e: print(f"Preview error: {e}")

    def export_file(self):
        self.project_manager.export_input_file(self.preview_text.get("1.0", tk.END))
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import subprocess
import threading

class ExecutionPanel(ttk.LabelFrame): # Changed to ttk.LabelFrame
    def __init__(self, parent_widget, controller):
        super().__init__(parent_widget, text="3. Execution Manager", padding=5)
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        # Configure grid for resizing
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1) # Main content area
        
        main_content = ttk.Frame(self)
        main_content.pack(fill="both", expand=True)

        # --- Top Inputs ---
        container = ttk.Frame(main_content)
        container.pack(side="top", fill="x", pady=5)

        # Exe Row
        r1 = ttk.Frame(container); r1.pack(fill="x", pady=2)
        ttk.Label(r1, text="NJOY Exe:", width=10, anchor="w").pack(side="left")
        self.ent_exe = ttk.Entry(r1)
        self.ent_exe.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_browse_exe = ttk.Button(r1, text="Browse...", command=self.browse_exe)
        self.btn_browse_exe.pack(side="right")

        # Dir Row
        r2 = ttk.Frame(container); r2.pack(fill="x", pady=2)
        ttk.Label(r2, text="Output Dir:", width=10, anchor="w").pack(side="left")
        self.ent_dir = ttk.Entry(r2)
        self.ent_dir.insert(0, self.controller.output_dir_path)
        self.ent_dir.pack(side="left", fill="x", expand=True, padx=5)
        self.btn_browse_dir = ttk.Button(r2, text="Browse...", command=self.browse_output_dir)
        self.btn_browse_dir.pack(side="right")

        # --- Bottom Area (Status + Button) ---
        bottom_frame = ttk.Frame(main_content)
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 0))

        self.status_var = tk.StringVar(value="Status: Idle")
        self.lbl_status = tk.Label(bottom_frame, textvariable=self.status_var, fg="gray", font=("Arial", 9, "italic"))
        self.lbl_status.pack(side="top", pady=(0, 5))

        self.btn_run = tk.Button(bottom_frame, text="🚀 LAUNCH NJOY", command=self.start_njoy_thread, 
                                 bg="orange", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_run.pack(side="bottom", fill="x")

    def browse_exe(self):
        f = filedialog.askopenfilename(title="Locate NJOY Executable")
        if f:
            self.ent_exe.delete(0, tk.END)
            self.ent_exe.insert(0, f)
            self.controller.njoy_exe_path = f

    def browse_output_dir(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            self.ent_dir.delete(0, tk.END)
            self.ent_dir.insert(0, d)
            self.controller.output_dir_path = d

    def _toggle_ui_state(self, is_running):
        state = "disabled" if is_running else "normal"
        self.ent_exe.config(state=state)
        self.ent_dir.config(state=state)
        self.btn_browse_exe.config(state=state)
        self.btn_browse_dir.config(state=state)
        self.btn_run.config(state=state)
        
        if is_running:
            self.btn_run.config(text="Running...", bg="#cccccc")
            self.lbl_status.config(fg="blue")
            self.status_var.set("Status: Calculation in progress...")
        else:
            self.btn_run.config(text="🚀 LAUNCH NJOY", bg="orange")
            self.lbl_status.config(fg="gray")

    def start_njoy_thread(self):
        exe = self.ent_exe.get()
        out_dir = self.ent_dir.get()
        
        if not exe or not os.path.exists(exe):
            messagebox.showerror("Error", "Invalid NJOY Executable path.")
            return
        if not out_dir:
            messagebox.showerror("Error", "Please select an output directory.")
            return
        
        if not os.path.exists(out_dir):
            try: os.makedirs(out_dir)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create directory:\n{e}")
                return

        self._toggle_ui_state(is_running=True)
        inp_content = self.controller.preview_text.get("1.0", tk.END)
        user_tapes = self.controller.user_tapes.copy()

        thread = threading.Thread(target=self._run_njoy_process, args=(exe, out_dir, inp_content, user_tapes))
        thread.daemon = True
        thread.start()

    def _run_njoy_process(self, exe, out_dir, inp_content, user_tapes):
        result = {"success": False, "msg": "", "returncode": None}
        inp_path = os.path.join(out_dir, "input.inp")
        
        try:
            with open(inp_path, "w") as f: f.write(inp_content)
            for unit, src_path in user_tapes.items():
                dst_name = f"tape{unit}"
                dst_path = os.path.join(out_dir, dst_name)
                if os.path.exists(dst_path): os.remove(dst_path)
                shutil.copy(src_path, dst_path)

            cmd = [exe]
            with open(inp_path, "r") as stdin_f:
                proc = subprocess.run(cmd, stdin=stdin_f, cwd=out_dir, capture_output=True, text=True)
            
            with open(os.path.join(out_dir, "output.log"), "w") as log: log.write(proc.stdout)
            if proc.stderr:
                with open(os.path.join(out_dir, "error.log"), "w") as err: err.write(proc.stderr)

            result["returncode"] = proc.returncode
            if proc.returncode == 0:
                result["success"] = True
                result["msg"] = f"NJOY Run Complete!\nFiles are in: {out_dir}"
            else:
                result["success"] = False
                tail = "\n".join(proc.stdout.splitlines()[-20:]) if proc.stdout else "No output."
                result["msg"] = f"NJOY Execution Failed (Code {proc.returncode})\n\nLast Output:\n{tail}"

        except Exception as e:
            result["success"] = False
            result["msg"] = f"System Error:\n{str(e)}"

        self.after(0, lambda: self._on_process_complete(result))

    def _on_process_complete(self, result):
        self._toggle_ui_state(is_running=False)
        if result["success"]:
            self.status_var.set("Status: Finished Successfully")
            self.lbl_status.config(fg="green")
            messagebox.showinfo("Success", result["msg"])
        else:
            self.status_var.set("Status: Failed")
            self.lbl_status.config(fg="red")
            messagebox.showerror("Execution Error", result["msg"])
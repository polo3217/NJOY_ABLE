import tkinter as tk
from tkinter import ttk

# ==============================================================================
# 1. TOOLTIP CLASS
# ==============================================================================
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 20
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 8, "normal"), padx=3, pady=1)
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ==============================================================================
# 2. COLLAPSIBLE FRAME (COMPACT)
# ==============================================================================
class CollapsibleFrame(ttk.Frame):
    def __init__(self, parent, title="", help_command=None, show_delete=True, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.showing = True
        self.columnconfigure(0, weight=1)
        
        # --- Title Header (Reduced Padding) ---
        self.title_frame = ttk.Frame(self, relief="groove", padding=(1, 1))
        self.title_frame.grid(row=0, column=0, sticky="ew")
        
        # Smaller Toggle Button
        self.toggle_btn = ttk.Button(self.title_frame, text="▼", width=2, command=self.toggle)
        self.toggle_btn.pack(side="left")
        
        # Smaller Font for Title
        self.title_lbl = ttk.Label(self.title_frame, text=title, font=("Segoe UI", 8, "bold"))
        self.title_lbl.pack(side="left", fill="x", expand=True, padx=2)
        
        # Help Button
        if help_command:
            btn = tk.Button(self.title_frame, text="?", width=2, command=help_command, 
                            relief="flat", fg="blue", cursor="hand2", font=("Arial", 7, "bold"), pady=0)
            btn.pack(side="right", padx=1)
            
        # Delete Button
        if show_delete:
            self.del_btn = tk.Button(self.title_frame, text="✕", fg="red", relief="flat", 
                                     bg="#e1e1e1", cursor="hand2", font=("Arial", 7, "bold"), pady=0)
            self.del_btn.pack(side="right", padx=1)
        else:
            self.del_btn = None

        # --- Content Container (Reduced Indentation) ---
        # Padding reduced from (10, 5) to (5, 2)
        self.sub_frame = ttk.Frame(self, padding=(5, 2))
        self.sub_frame.grid(row=1, column=0, sticky="nsew")

    def toggle(self):
        if self.showing:
            self.sub_frame.grid_remove()
            self.toggle_btn.configure(text="►")
            self.showing = False
        else:
            self.sub_frame.grid()
            self.toggle_btn.configure(text="▼")
            self.showing = True

# ==============================================================================
# 3. SMART INPUT ROW (COMPACT)
# ==============================================================================
class SmartInputRow(ttk.Frame):
    def __init__(self, parent, inp_obj, update_callback, options_callback=None, help_callback=None):
        super().__init__(parent)
        self.inp_obj = inp_obj
        self.update_callback = update_callback
        self.options_callback = options_callback
        
        self.columnconfigure(1, weight=1) 
        
        # 1. Label (Reduced width, Smaller Font handled by global style)
        lbl = ttk.Label(self, text=inp_obj.name, width=18, anchor="w")
        # pady=0 makes rows touch each other
        lbl.grid(row=0, column=0, sticky="w", padx=(0, 2), pady=0)
        
        # 2. Entry
        self.var = tk.StringVar(value=str(inp_obj.value))
        self.var.trace_add("write", self.on_change)
        
        self.entry = ttk.Entry(self, textvariable=self.var, font=("Segoe UI", 8))
        self.entry.grid(row=0, column=1, sticky="ew", pady=0)
        
        # 3. Option Button
        col_idx = 2
        if inp_obj.options:
            opt_btn = tk.Button(self, text="≡", width=2, relief="flat", bg="#f0f0f0",
                                font=("Arial", 7), pady=0,
                                command=lambda: self.options_callback(inp_obj, self.var, inp_obj.options))
            opt_btn.grid(row=0, column=col_idx, padx=1)
            col_idx += 1

        # 4. Question Mark Button
        def trigger_help():
            if help_callback:
                help_callback(f"Input: {inp_obj.name}", inp_obj.description, inp_obj.ref)

        q_btn = tk.Button(self, text="?", width=2, relief="flat", fg="blue", 
                          cursor="hand2", font=("Arial", 7, "bold"), pady=0,
                          command=trigger_help)
        q_btn.grid(row=0, column=col_idx, padx=(1,0))

        self.validate_visuals()

    def on_change(self, *args):
        self.inp_obj.value = self.var.get()
        self.validate_visuals()
        if self.update_callback:
            self.update_callback()

    def validate_visuals(self):
        if self.inp_obj.validate():
            self.entry.configure(foreground="black")
        else:
            self.entry.configure(foreground="red")
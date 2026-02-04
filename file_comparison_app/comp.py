import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import difflib

class NJOYProDiff(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("NJOY Data Validator // Professional File Comparison")
        self.geometry("1200x800")
        ctk.set_appearance_mode("dark")
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1) 
        self.grid_rowconfigure(2, weight=0) 

        # --- Top Menu (Navigation) ---
        self.menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.menu_frame.grid(row=0, column=0, columnspan=2, pady=15, padx=20, sticky="ew")
        
        self.btn_file1 = ctk.CTkButton(self.menu_frame, text="Load Base File", 
                                       command=lambda: self.load_file(1), fg_color="#3b3b3b")
        self.btn_file1.pack(side="left", padx=5)

        self.btn_file2 = ctk.CTkButton(self.menu_frame, text="Load Comparison", 
                                       command=lambda: self.load_file(2), fg_color="#3b3b3b")
        self.btn_file2.pack(side="left", padx=5)

        self.btn_reset = ctk.CTkButton(self.menu_frame, text="New Comparison", 
                                       command=self.reset_session, fg_color="#722f37", hover_color="#a23c48")
        self.btn_reset.pack(side="right", padx=5)

        # --- Main Comparison Area ---
        self.main_container = ctk.CTkFrame(self)
        self.main_container.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="nsew")
        self.main_container.grid_columnconfigure((1, 3), weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Left Gutter (Line Numbers) & Text
        self.line_nums_l = tk.Text(self.main_container, width=5, padx=5, pady=10, fg="#666666", 
                                   bg="#1a1a1a", borderwidth=0, font=("Courier New", 12), state="disabled")
        self.line_nums_l.grid(row=0, column=0, sticky="ns")
        
        self.txt_left = tk.Text(self.main_container, wrap="none", bg="#242424", fg="#ffffff", 
                                font=("Courier New", 12), borderwidth=0, state="disabled")
        self.txt_left.grid(row=0, column=1, sticky="nsew")

        # Right Gutter (Line Numbers) & Text
        self.line_nums_r = tk.Text(self.main_container, width=5, padx=5, pady=10, fg="#666666", 
                                   bg="#1a1a1a", borderwidth=0, font=("Courier New", 12), state="disabled")
        self.line_nums_r.grid(row=0, column=2, sticky="ns")

        self.txt_right = tk.Text(self.main_container, wrap="none", bg="#242424", fg="#ffffff", 
                                 font=("Courier New", 12), borderwidth=0, state="disabled")
        self.txt_right.grid(row=0, column=3, sticky="nsew")

        # Shared Scrollbar
        self.master_scroll = ctk.CTkScrollbar(self.main_container, command=self.sync_scroll)
        self.master_scroll.grid(row=0, column=4, sticky="ns")
        
        # Linking scrolling
        self.txt_left.config(yscrollcommand=self.master_scroll.set)
        self.txt_right.config(yscrollcommand=self.master_scroll.set)

        # --- Footer (Status Bar) ---
        self.status_frame = ctk.CTkFrame(self, height=35, fg_color="#1a1a1a")
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        self.lbl_stats = ctk.CTkLabel(self.status_frame, text="Status: Waiting for files...", 
                                      font=("Segoe UI", 12))
        self.lbl_stats.pack(side="left", padx=20)

        # --- Internal Logic ---
        self.file1_content = []
        self.file2_content = []

        # Highlighting Styles
        self.txt_left.tag_config("removal", background="#4a2c2c", foreground="#ff9999")
        self.txt_right.tag_config("addition", background="#2c4a2c", foreground="#99ff99")

    def sync_scroll(self, *args):
        """Unified scrolling for all four text widgets."""
        self.txt_left.yview(*args)
        self.txt_right.yview(*args)
        self.line_nums_l.yview(*args)
        self.line_nums_r.yview(*args)

    def load_file(self, slot):
        path = filedialog.askopenfilename(title=f"Select File {slot}")
        if not path: return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.readlines()
        except Exception as e:
            self.lbl_stats.configure(text=f"Error: Could not read file. {e}")
            return
        
        if slot == 1:
            self.file1_content = content
            self.lbl_stats.configure(text="Base File loaded. Load Comparison File to proceed.")
        else:
            self.file2_content = content
            self.lbl_stats.configure(text="Comparison File loaded.")
        
        if self.file1_content and self.file2_content:
            self.run_diff()

    def run_diff(self):
        """Calculates differences and populates the UI."""
        # Unlock all
        for w in [self.txt_left, self.txt_right, self.line_nums_l, self.line_nums_r]:
            w.config(state="normal")
            w.delete("1.0", tk.END)

        d = difflib.Differ()
        diff = list(d.compare(self.file1_content, self.file2_content))

        ln_l, ln_r = 1, 1
        total_diffs = 0

        for line in diff:
            status = line[0]
            text = line[2:]

            if status == ' ': # Matching
                self.line_nums_l.insert(tk.END, f"{ln_l}\n")
                self.line_nums_r.insert(tk.END, f"{ln_r}\n")
                self.txt_left.insert(tk.END, text)
                self.txt_right.insert(tk.END, text)
                ln_l += 1; ln_r += 1
            elif status == '-': # Deletion
                total_diffs += 1
                self.line_nums_l.insert(tk.END, f"{ln_l}\n")
                self.line_nums_r.insert(tk.END, " \n") # Keep sync
                self.txt_left.insert(tk.END, text, "removal")
                self.txt_right.insert(tk.END, "\n")
                ln_l += 1
            elif status == '+': # Addition
                total_diffs += 1
                self.line_nums_l.insert(tk.END, " \n") # Keep sync
                self.line_nums_r.insert(tk.END, f"{ln_r}\n")
                self.txt_left.insert(tk.END, "\n")
                self.txt_right.insert(tk.END, text, "addition")
                ln_r += 1

        # Re-lock all
        for w in [self.txt_left, self.txt_right, self.line_nums_l, self.line_nums_r]:
            w.config(state="disabled")

        self.lbl_stats.configure(text=f"Analysis Complete: Found {total_diffs} differences.")

    def reset_session(self):
        """Clears memory and wipes the UI for a fresh comparison."""
        self.file1_content = []
        self.file2_content = []
        
        for w in [self.txt_left, self.txt_right, self.line_nums_l, self.line_nums_r]:
            w.config(state="normal")
            w.delete("1.0", tk.END)
            w.config(state="disabled")
            
        self.lbl_stats.configure(text="Session Reset. Load new files.")

if __name__ == "__main__":
    app = NJOYProDiff()
    app.mainloop()
import tkinter as tk
from tkinter import ttk

class UIUtils:
    @staticmethod
    def show_info(root, title, description, ref):
        top = tk.Toplevel(root)
        top.title(f"Help: {title}")
        top.geometry("600x400")
        
        tk.Label(top, text=title, font=("Segoe UI", 12, "bold"), pady=5).pack()
        
        f = tk.Frame(top, padx=5, pady=5)
        f.pack(fill="both", expand=True)
        
        txt = tk.Text(f, wrap="word", font=("Segoe UI", 11), bg="#f0f0f0", relief="flat", padx=5, pady=5)
        txt.pack(side="left", fill="both", expand=True)
        
        scroll = ttk.Scrollbar(f, orient="vertical", command=txt.yview)
        scroll.pack(side="right", fill="y")
        txt.configure(yscrollcommand=scroll.set)
        
        txt.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        txt.insert("end", "DESCRIPTION:\n", "bold")
        txt.insert("end", f"{description or 'N/A'}\n\n")
        txt.insert("end", "REFERENCE:\n", "bold")
        txt.insert("end", f"{ref or 'N/A'}")
        
        txt.config(state="disabled")
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=5)

    @staticmethod
    def open_selection_list(root, inp_obj, tk_var, options_dict):
        top = tk.Toplevel(root)
        top.title(f"Select {inp_obj.name}")
        top.geometry("400x500") 
        
        search_frame = tk.Frame(top, padx=5, pady=5)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="Filter:").pack(side="left")
        search_var = tk.StringVar()
        entry = ttk.Entry(search_frame, textvariable=search_var)
        entry.pack(side="left", fill="x", expand=True, padx=5)
        
        lb = tk.Listbox(top)
        lb.pack(fill="both", expand=True, padx=5, pady=5)
        
        all_items = [f"{k} : {v}" for k, v in options_dict.items()]
        
        def pop(filt=""):
            lb.delete(0, tk.END)
            for i in all_items: 
                if filt.lower() in i.lower(): lb.insert(tk.END, i)
        pop()
        
        search_var.trace_add("write", lambda *a: pop(search_var.get()))
        
        def sel():
            if lb.curselection():
                tk_var.set(lb.get(lb.curselection()[0]).split(" : ")[0])
                top.destroy()
        
        tk.Button(top, text="Select", command=sel).pack(fill="x", padx=5, pady=5)

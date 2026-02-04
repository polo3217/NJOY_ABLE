import json
import os
from tkinter import filedialog, messagebox

class ProjectManager:
    """
    Handles serialization (Saving) and deserialization (Loading) of the project state.
    """
    def __init__(self, parent_app, available_modules):
        self.parent = parent_app
        self.AVAILABLE_MODULES = available_modules

    def save_project(self):
        data = []
        for mod in self.parent.active_modules:
            # Identify class type
            mod_type_key = None
            for key, cls in self.AVAILABLE_MODULES.items():
                if isinstance(mod, cls):
                    mod_type_key = key
                    break
            
            if not mod_type_key: continue

            # Serialize Cards
            cards_data = {}
            for card in mod.cards:
                inputs_data = {}
                for inp in card.inputs:
                    inputs_data[inp.name] = inp.value
                cards_data[card.name] = inputs_data
            
            data.append({
                "type": mod_type_key,
                "cards": cards_data
            })

        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("NJOY Project", "*.json")])
        if path:
            try:
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", f"Project saved to {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def load_project(self):
        path = filedialog.askopenfilename(filetypes=[("NJOY Project", "*.json")])
        if not path: return

        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            # Clear UI
            for mod in self.parent.active_modules:
                if hasattr(mod, 'cached_widget'):
                    mod.cached_widget.destroy()
            self.parent.active_modules = []
            
            # Rebuild
            for mod_entry in data:
                mod_type = mod_entry.get("type")
                if mod_type not in self.AVAILABLE_MODULES: continue
                
                new_mod = self.AVAILABLE_MODULES[mod_type]()
                saved_cards = mod_entry.get("cards", {})

                # Pass 1: Initialize Control Variables
                self._apply_data_to_module(new_mod, saved_cards)

                # Regenerate Structure
                if hasattr(new_mod, "regenerate"):
                    new_mod.regenerate()

                # Pass 2: Fill Dynamic Data
                self._apply_data_to_module(new_mod, saved_cards)

                # Add to UI
                new_mod.cached_widget = self.parent._create_module_widget(new_mod)
                self.parent.active_modules.append(new_mod)

            self.parent.reorder_modules_layout()
            self.parent.update_preview()
            messagebox.showinfo("Success", "Project loaded successfully.")

        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _apply_data_to_module(self, module, saved_cards):
        for card in module.cards:
            if card.name in saved_cards:
                for inp in card.inputs:
                    if inp.name in saved_cards[card.name]:
                        inp.value = saved_cards[card.name][inp.name]

    def export_input_file(self, content):
        path = filedialog.asksaveasfilename(defaultextension=".inp", filetypes=[("NJOY Input", "*.inp")])
        if path:
            try:
                with open(path, "w") as f: f.write(content)
                messagebox.showinfo("Success", f"Saved to {path}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))
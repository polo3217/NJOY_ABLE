from class_def import NjoyCard, NjoyInput
import Data_bases 

# ==============================================================================
# 2. MODULE DEFINITIONS
# ==============================================================================
class Reconr:
    def __init__(self):
        self.name = "reconr"
        self.description = (
            "RECONR (Resonance Reconstruction) is the foundation of NJOY processing.\n"
            "Raw nuclear data (ENDF) contains 'Resonance Parameters' (formulas) to save space.\n"
            "RECONR expands these formulas into a dense 'Pointwise' grid (Energy vs. Cross-Section).\n"
            "Output: A PENDF (Pointwise ENDF) file used by all subsequent modules."
        )
        self.ref = "NJOY2016 Manual, Section 4, Page 36"
        self.cards = []

        # ======================================================================
        # 1. LOGIC HELPERS
        # ======================================================================
        def is_int(x):
            try: return int(x) or True
            except: return False
            
        def is_float(x):
            try: return float(x) or True
            except: return False

        def get_nmat():
            """Returns number of materials the user wants to process."""
            try:
                val = int(self.c2.nmat.value)
                return max(1, val)
            except:
                return 1

        def is_mat_active_factory(index):
            """Show Material Block #i only if index <= requested NMAT."""
            return lambda: index <= get_nmat()

        # --- UPDATED: Visibility for specific Comment Line J ---
        def is_comment_active_factory(mat_idx, comm_idx):
            def check():
                # 1. Check if material is active
                if not is_mat_active_factory(mat_idx)(): return False
                try:
                    # 2. Check if ncards >= current comment index
                    c3_card = getattr(self, f"c3_{mat_idx}")
                    ncards_inp = getattr(c3_card, f"ncards_{mat_idx}")
                    return int(ncards_inp.value) >= comm_idx
                except:
                    return False
            return check

        def is_card6_active_factory(index):
            """Show User Grid only if user requested NGRID > 0."""
            def check():
                if not is_mat_active_factory(index)(): return False
                try:
                    card = getattr(self, f"c3_{index}")
                    inp = getattr(card, f"ngrid_{index}")
                    return int(inp.value) > 0
                except:
                    return False
            return check

        # ======================================================================
        # 2. CARD DEFINITIONS
        # ======================================================================
        
        # --- Card 1: Units ---
        c1 = NjoyCard("c1", "I/O Configuration", "Page 36")
        
        nendf_desc = (
            "Input Tape (NENDF).\n"
            "The tape number containing your raw source data (ENDF format).\n"
            "Usually Tape 20 or similar."
        )
        c1.add_input(NjoyInput("nendf", nendf_desc, 20, rule=is_int, is_input_file=True, ref="Page 36"))
        
        npend_desc = (
            "Output Tape (NPEND).\n"
            "The tape number where the new Pointwise (linearized) data will be saved.\n"
            "This tape (e.g., 21) will be the input for BROADR or HEATR."
        )
        c1.add_input(NjoyInput("npend", npend_desc, 21, rule=is_int, is_output_file=True, ref="Page 36"))
        
        self.add_card(c1, "c1") 

        # --- Card 2: Label & Count ---
        c2 = NjoyCard("c2", "Run Control", "Page 36")
        
        tlabel_desc = (
            "Tape Label (TLABEL).\n"
            "A 66-character descriptive title for the new PENDF tape.\n"
            "Example: 'U-235 ENDF/B-VIII.0 Linearized at 0K'."
        )
        c2.add_input(NjoyInput("tlabel", tlabel_desc, "PENDF TAPE", ref="Page 36"))
        
        nmat_desc = (
            "Number of Materials (NMAT).\n"
            "How many isotopes do you want to process from the input tape?\n"
            "Entering '2' will generate two sets of material cards below."
        )
        c2.add_input(NjoyInput("nmat", nmat_desc, 1, rule=is_int))
        self.add_card(c2, "c2") 

        # --- MATERIAL LOOP (Generates slots for up to 5 materials) ---
        for i in range(1, 6): 
            active_chk = is_mat_active_factory(i)
            
            # --- Card 3: Material Control ---
            c3 = NjoyCard(f"c3_{i}", f"Mat #{i}: Selection", "Page 36", active_if=active_chk)
            
            mat_desc = (
                "Material ID (MAT).\n"
                "The specific integer ID of the isotope (e.g., 9228 for U-235).\n"
                "Use the 'Select' button (≡) to browse the library."
            )
            c3.add_input(NjoyInput(f"mat_{i}", mat_desc, 125, rule=is_int, ref="Page 36", options=Data_bases.MAT_DB))
            
            ncards_desc = (
                "Header Cards (NCARDS).\n"
                "How many lines of text do you want to add to the file header?\n"
                "Set to 0 if no extra comments are needed. In the GUI 10 maximum."
            )
            c3.add_input(NjoyInput(f"ncards_{i}", ncards_desc, 0, rule=is_int, ref="Page 36"))
            
            ngrid_desc = (
                "Extra Grid Points (NGRID).\n"
                "Number of fixed energy points to force into the grid.\n"
                "Usually 0. Set to >0 to enable the 'User Grid' card."
            )
            c3.add_input(NjoyInput(f"ngrid_{i}", ngrid_desc, 0, rule=is_int, ref="Page 36"))
            
            self.add_card(c3, f"c3_{i}")

            # --- Card 4: Tolerances ---
            c4 = NjoyCard(f"c4_{i}", f"Mat #{i}: Precision", "Page 37", active_if=active_chk)
            
            err_desc = (
                "Reconstruction Tolerance (ERR).\n"
                "The allowed error between the linear fit and the real curve.\n"
                " • 0.005 (0.5%): Standard for general physics.\n"
                " • 0.001 (0.1%): High precision (Reference)."
            )
            c4.add_input(NjoyInput(f"err_{i}", err_desc, 0.005, rule=is_float))
            
            tempr_desc = (
                "Temperature (TEMPR).\n"
                "Reconstruction temperature in Kelvin.\n"
                "Always 0.0 K for RECONR. Doppler broadening is done later (BROADR)."
            )
            c4.add_input(NjoyInput(f"tempr_{i}", tempr_desc, 0.0, rule=is_float))
            
            errmax_desc = "Max Resonance Error. Default = 10 * ERR. (Leave blank for default)"
            c4.add_input(NjoyInput(f"errmax_{i}", errmax_desc, "", rule=is_float))
            
            errint_desc = "Max Integral Error. Default = ERR / 20000. (Leave blank for default)"
            c4.add_input(NjoyInput(f"errint_{i}", errint_desc, "", rule=is_float))
            
            self.add_card(c4, f"c4_{i}")

            # --- Card 5: Comments (Dynamic Slots) ---
            # Creates 10 potential comment cards. 
            # They will show/hide automatically based on the 'ncards' value above.
            for j in range(1, 11):
                # Unique visibility check for each line
                comm_active_chk = is_comment_active_factory(i, j)
                
                c5 = NjoyCard(f"comment_{i}_{j}", f"Mat #{i}: Comment Line {j}", "Page 37", active_if=comm_active_chk)
                
                # Input field
                c5.add_input(NjoyInput(f"cards5_{i}_{j}", "Comment Text", "", ref="Page 37"))
                
                self.add_card(c5, f"c5_{i}_{j}")

            # --- Card 6: User Grid ---
            c6 = NjoyCard(f"c6_{i}", f"Mat #{i}: User Grid", "Page 37", active_if=is_card6_active_factory(i))
            
            enode_desc = (
                "Energy Anchors (ENODE).\n"
                "Select a standard grid (≡) or type values (comma separated).\n"
                "Used to ensure the grid includes specific threshold energies."
            )
            c6.add_input(NjoyInput(f"enode_{i}", enode_desc, "", ref="Page 37", options=Data_bases.GRID_DB))
            
            self.add_card(c6, f"c6_{i}")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name:
            setattr(self, name, card)

    def write(self):
        """Custom write method for RECONR due to complex dependencies."""
        lines = [self.name]
        
        # --- Card 1 ---
        lines.append(f"{self.c1.nendf.value} {self.c1.npend.value}/")
        
        # --- Card 2 ---
        lbl = str(self.c2.tlabel.value).strip()
        if not (lbl.startswith("'") and lbl.endswith("'")): lbl = f"'{lbl}'"
        lines.append(f"{lbl}/")

        # --- Material Loop ---
        try: nmat = int(self.c2.nmat.value)
        except: nmat = 1
        
        for i in range(1, nmat + 1):
            c3 = getattr(self, f"c3_{i}")
            c4 = getattr(self, f"c4_{i}")
            c6 = getattr(self, f"c6_{i}")
            
            mat = getattr(c3, f"mat_{i}").value
            ncards = int(getattr(c3, f"ncards_{i}").value or 0)
            ngrid = int(getattr(c3, f"ngrid_{i}").value or 0)
            
            err = getattr(c4, f"err_{i}").value
            tempr = getattr(c4, f"tempr_{i}").value
            
            # --- Calculated Defaults (Card 4) ---
            errmax_val = getattr(c4, f"errmax_{i}").value
            if errmax_val is None or str(errmax_val).strip() == "":
                try: errmax = float(err) * 10
                except: errmax = 0.05
            else:
                errmax = errmax_val
            
            errint_val = getattr(c4, f"errint_{i}").value
            if errint_val is None or str(errint_val).strip() == "":
                try: errint = float(err) / 20000
                except: errint = 1e-6
            else:
                errint = errint_val

            lines.append(f"{mat} {ncards} {ngrid}/")
            lines.append(f"{err} {tempr} {errmax} {errint}/")
            
            # --- Card 5: Comments Formatting (UPDATED) ---
            if ncards > 0:
                for j in range(1, ncards + 1):
                    try:
                        # Find the specific comment card for this index
                        c5_card = getattr(self, f"c5_{i}_{j}")
                        c5_input = getattr(c5_card, f"cards5_{i}_{j}")
                        
                        txt = str(c5_input.value)
                        if not (txt.startswith("'") and txt.endswith("'")): txt = f"'{txt}'"
                        lines.append(f"{txt}/")
                    except AttributeError:
                        lines.append("'Blank Comment'/")
            
            # --- Card 6: Grid Formatting ---
            if ngrid > 0:
                raw_enode = str(getattr(c6, f"enode_{i}").value)
                if raw_enode in Data_bases.GRID_DB:
                    clean_enode = Data_bases.GRID_DB[raw_enode]
                else:
                    clean_enode = raw_enode.replace(",", " ")
                lines.append(f"{clean_enode}/")

        lines.append("0/") 
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nendf.value]

    @property
    def output_files(self): return [self.c1.npend.value]
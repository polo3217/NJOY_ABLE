from class_def import NjoyCard, NjoyInput
import Data_bases 

class Broadr:
    def __init__(self):
        self.name = "broadr"
        self.description = (
            "BROADR (Doppler Broadening) adds temperature effects to cross-sections.\n"
            "It simulates the thermal motion of target nuclei, which causes resonances to 'widen' "
            "and cross-sections to change shape.\n\n"
            "Input: A PENDF tape (usually from RECONR) at 0 Kelvin.\n"
            "Output: A new PENDF tape containing data at higher temperatures (e.g., 300K, 600K)."
        )
        self.ref = "NJOY2016 Manual, Section 5, Page 45"
        self.cards = []
        
        # Initialize structure
        self.regenerate()

    def regenerate(self):
        # 1. PRESERVE STATE (NMAT)
        current_nmat = 1
        if hasattr(self, 'c_gui') and hasattr(self.c_gui, 'nmat'):
            try: current_nmat = int(self.c_gui.nmat.value)
            except: pass
        
        self.cards = []

        # ======================================================================
        # 1. LOGIC HELPERS
        # ======================================================================
        def is_int(x):
            try: return int(x) or True
            except: return False
            
        def is_float(x):
            try: 
                # sanitize for scientific notation like 1.0-5 or 1.0+5 commonly used in ENDF
                val = str(x).lower().replace('d', 'e')
                return float(val) or True
            except: return False

        def get_nmat():
            try: return max(1, int(self.c_gui.nmat.value))
            except: return 1

        def is_mat_active_factory(index):
            return lambda: index <= get_nmat()

        def validate_temp_count_factory(index):
            """Checks if the number of temperatures entered matches NTEMP2."""
            def check(value):
                try:
                    # Access Card 2 to get ntemp2
                    c2_card = getattr(self, f"c2_{index}")
                    ntemp_inp = getattr(c2_card, f"ntemp2_{index}")
                    required_count = int(ntemp_inp.value)
                    
                    values = str(value).replace(",", " ").split()
                    return len(values) == required_count
                except:
                    return False
            return check

        # ======================================================================
        # 2. CARD DEFINITIONS
        # ======================================================================
        
        # --- Card 1: I/O Units ---
        c1 = NjoyCard("c1", "Card 1: I/O Configuration", "Page 45")
        
        nendf_desc = (
            "Input ENDF Tape (NENDF).\n"
            "The unit number of the original ENDF tape (e.g., 20).\n"
            "Used to read standard atomic weights and check consistency."
        )
        c1.add_input(NjoyInput("nendf", nendf_desc, 20, rule=is_int, is_input_file=True, ref="Page 45"))
        
        nin_desc = (
            "Input PENDF Tape (NIN).\n"
            "The unit number containing the input data.\n"
            "Typically the output from RECONR (0 Kelvin data)."
        )
        c1.add_input(NjoyInput("nin", nin_desc, 21, rule=is_int, is_input_file=True, ref="Page 45"))
        
        nout_desc = (
            "Output PENDF Tape (NOUT).\n"
            "The unit number where the new, Doppler-broadened data will be saved.\n"
            "This file can be used as input for THERMR or GROUPR."
        )
        c1.add_input(NjoyInput("nout", nout_desc, 22, rule=is_int, is_output_file=True, ref="Page 45"))
        
        self.add_card(c1, "c1") 

        # --- GUI Control (Hidden) ---
        c_gui = NjoyCard("c_gui", "GUI Setup", "Page 45")
        nmat_desc = "Number of Materials to process (Controls GUI loops only)."
        c_gui.add_input(NjoyInput("nmat", nmat_desc, current_nmat, rule=is_int, hidden_in_file=True))
        self.add_card(c_gui, "c_gui")

        # --- MATERIAL LOOP ---
        for i in range(1, current_nmat + 1): 
            active_chk = is_mat_active_factory(i)
            
            # --- Card 2: Material & Temperature Control ---
            c2 = NjoyCard(f"c2_{i}", f"Card 2 (Mat {i}): Control", "Page 45", active_if=active_chk)
            
            mat_desc = (
                "Material ID (MAT1).\n"
                "The integer ID of the isotope to broaden (e.g., 9228 for U-235).\n"
                "Must match the material on the input PENDF tape."
            )
            c2.add_input(NjoyInput(f"mat1_{i}", mat_desc, 125, rule=is_int, ref="Page 45 (MAT1)", options=Data_bases.MAT_DB))
            
            ntemp_desc = (
                "Number of Final Temperatures (NTEMP2).\n"
                "How many new temperature datasets do you want to create?\n"
                "Example: Enter '2' to create data at 300K and 600K."
            )
            c2.add_input(NjoyInput(f"ntemp2_{i}", ntemp_desc, 1, rule=is_int, ref="Page 45 (NTEMP2)"))
            
            istrt_desc = (
                "Restart Option (ISTART).\n"
                "• 0 = Standard. Start from the base temperature (STOP, usually 0K) found on the input tape.\n"
                "• 1 = Restart. The input tape already contains broadened data. We will add more temperatures to it."
            )
            c2.add_input(NjoyInput(f"istart_{i}", istrt_desc, 0, rule=is_int, ref="Page 45 (ISTART)"))
            
            istrap_desc = (
                "Bootstrap Option (ISTRAP).\n"
                "Controls calculation efficiency.\n"
                "• 0 = Yes (Bootstrap). Calculate 300K from 0K, then 600K from 300K. Efficient.\n"
                "• 1 = No (Direct). Calculate 300K from 0K, then 600K from 0K. Slower, strictly precise.\n"
                "Default: 0."
            )
            c2.add_input(NjoyInput(f"istrap_{i}", istrap_desc, 0, rule=is_int, ref="Page 45 (ISTRAP)"))
            
            temp1_desc = (
                "Initial Temperature (temp1/TEMP1).\n"
                "The temperature of the data on the input PENDF tape.\n"
                "Usually 0.0 K assuming input is from RECONR.\n"
                "Format: Float (e.g., 0.0, 1.0e-5)."
            )
            c2.add_input(NjoyInput(f"temp1_{i}", temp1_desc, 0.0, rule=is_float, ref="Page 45 (temp1)"))
            
            self.add_card(c2, f"c2_{i}")

            # --- Card 3: Precision & Thinning ---
            c3 = NjoyCard(f"c3_{i}", f"Card 3 (Mat {i}): Tolerances", "Page 45", active_if=active_chk)
            
            errthn_desc = (
                "Thinning Tolerance (ERRTHN).\n"
                "After broadening, the code removes redundant points that can be interpolated linearly.\n"
                "• 0.005 (0.5%): Standard accuracy.\n"
                "• 0.001 (0.1%): High accuracy (larger files).\n"
                "Format: Float. Scientific notation allowed (e.g., 5e-3, 1.0e-4)."
            )
            c3.add_input(NjoyInput(f"errthn_{i}", errthn_desc, 0.005, rule=is_float, ref="Page 45 (ERRTHN)"))
            
            thnmax_desc = (
                "Max Energy (THNMAX).\n"
                "The upper energy limit (eV) for the broadening/thinning process.\n"
                "Above this energy, Doppler effects are negligible.\n"
                "Default: 1e6 (1 MeV). Format: Float (e.g., 1e6, 2.0e7)."
            )
            # UPDATED: Default is now "1e6" string to preserve formatting
            c3.add_input(NjoyInput(f"thnmax_{i}", thnmax_desc, "1e6", rule=is_float, ref="Page 45 (THNMAX)"))
            
            errint_desc = (
                "Integral Tolerance (ERRINT).\n"
                "Alternative tolerance for resonance integrals. Rarely changed.\n"
                "Default: ERRTHN / 10. (Leave blank to use default).\n"
                "Format: Float (e.g., 5e-4)."
            )
            c3.add_input(NjoyInput(f"errint_{i}", errint_desc, "", rule=is_float, ref="Page 45 (ERRINT)"))
            
            thn1_desc = (
                "Start Energy (THN1).\n"
                "The lower energy limit (eV) to begin processing.\n"
                "Default: 0.0 (Process entire energy range).\n"
                "Format: Float."
            )
            c3.add_input(NjoyInput(f"thn1_{i}", thn1_desc, 0.0, rule=is_float, ref="Page 45 (THN1)"))
            
            self.add_card(c3, f"c3_{i}")

            # --- Card 4: Temperatures ---
            c4 = NjoyCard(f"c4_{i}", f"Card 4 (Mat {i}): Temperature List", "Page 45", active_if=active_chk)
            
            temp_desc = (
                "Target Temperatures (TEMP).\n"
                "List the final temperatures you want to generate (in Kelvin).\n"
                "Separate values with spaces.\n"
                "Example: '293.6' or '300.0 600.0 900.0'.\n"
                "The number of values MUST match NTEMP2 on Card 2."
            )
            temp_rule = validate_temp_count_factory(i)
            c4.add_input(NjoyInput(f"temp_{i}", temp_desc, "293.6", rule=temp_rule, ref="Page 45 (TEMP)"))
            
            self.add_card(c4, f"c4_{i}")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        
        # --- Card 1 ---
        lines.append(f"{self.c1.nendf.value} {self.c1.nin.value} {self.c1.nout.value}/")
        
        # --- Loop ---
        try: nmat = int(self.c_gui.nmat.value)
        except: nmat = 1
        
        for i in range(1, nmat + 1):
            c2 = getattr(self, f"c2_{i}")
            c3 = getattr(self, f"c3_{i}")
            c4 = getattr(self, f"c4_{i}")
            
            # --- Card 2 Values ---
            mat1 = getattr(c2, f"mat1_{i}").value
            ntemp2 = getattr(c2, f"ntemp2_{i}").value
            istart = getattr(c2, f"istart_{i}").value
            istrap = getattr(c2, f"istrap_{i}").value
            temp1 = getattr(c2, f"temp1_{i}").value
            
            # Apply defaults for temp1 if missing
            if str(temp1).strip() == "": temp1 = 0.0
            
            # --- Card 3 Values ---
            errthn = getattr(c3, f"errthn_{i}").value
            
            # Defaults for Card 3
            thnmax_val = getattr(c3, f"thnmax_{i}").value
            # UPDATED: Fallback to "1e6" string to match requested format
            thnmax = thnmax_val if str(thnmax_val).strip() != "" else "1e6"
            
            errint_val = getattr(c3, f"errint_{i}").value
            # Default for ERRINT is usually handled by NJOY if blank, but we can explicitly set 0.0 or calculated
            errint = errint_val if str(errint_val).strip() != "" else 0.0
            
            thn1_val = getattr(c3, f"thn1_{i}").value
            thn1 = thn1_val if str(thn1_val).strip() != "" else 0.0

            # Write Card 2: MAT1 NTEMP2 ISTART ISTRAP temp1
            lines.append(f"{mat1} {ntemp2} {istart} {istrap} {temp1}/")
            
            # Write Card 3: ERRTHN THNMAX ERRINT THN1
            lines.append(f"{errthn} {thnmax} {errint} {thn1}/")
            
            # Write Card 4: TEMP List
            raw_temp = str(getattr(c4, f"temp_{i}").value)
            clean_temp = raw_temp.replace(",", " ")
            lines.append(f"{clean_temp}/")

        lines.append("0 /") 
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nin.value]

    @property
    def output_files(self): return [self.c1.nout.value]
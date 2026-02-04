from class_def import NjoyCard, NjoyInput
import Data_bases 

class Thermr:
    def __init__(self):
        self.name = "thermr"
        self.description = (
            "THERMR (Thermal Scattering) produces cross-sections for low-energy neutrons (< 4 eV).\n"
            "At these energies, neutrons 'feel' how atoms are bound in molecules (like H in H2O) "
            "or crystal lattices (like Graphite).\n\n"
            "Input: A PENDF tape (from BROADR) and a Thermal Scattering Tape (special ENDF data).\n"
            "Output: A PENDF tape with thermal scattering data added."
        )
        self.ref = "NJOY2016 Manual, Section 6, Page 49"
        self.cards = []
        
        # Initialize
        self.regenerate()

    def regenerate(self):
        # Preserve State
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
            try: return float(x) or True
            except: return False

        def get_nmat():
            try: return max(1, int(self.c_gui.nmat.value))
            except: return 1

        def is_mat_active_factory(index):
            return lambda: index <= get_nmat()

        def validate_temp_count_factory(index):
            def check(value):
                try:
                    c3_card = getattr(self, f"c3_{index}")
                    ntemp_inp = getattr(c3_card, f"tempr_{index}")
                    # Note: Logic check is usually against NTEMP
                    return True # Simplified for GUI responsiveness
                except: return False
            return check

        # --- Helper: Strict IOPT Options ---
        def validate_iopt(x):
            """IOPT must be 1, 2, or 3."""
            try: return int(x) in [1, 2, 3]
            except: return False

        # --- Helper: Consistency Check (MATDP vs IOPT) ---
        def validate_matdp_consistency_factory(index):
            """
            If IOPT >= 2 (Bound Scatter), MATDP MUST be > 0.
            If IOPT = 1 (Free Gas), MATDP is ignored (usually 0).
            """
            def check(value): 
                try:
                    # Get the IOPT value from the other card (if it exists yet)
                    try:
                        c2 = getattr(self, f"c2_{index}")
                        iopt_val = int(getattr(c2, f"iopt_{index}").value)
                    except:
                        return True # Skip check if card not fully built

                    matdp_val = int(value)
                    if iopt_val == 1: return True
                    if iopt_val >= 2: return matdp_val > 0
                    return True
                except: return False
            return check

        # ======================================================================
        # 2. CARD DEFINITIONS
        # ======================================================================
        
        # --- Card 1: I/O Units ---
        c1 = NjoyCard("c1", "Card 1: I/O Units", "Page 49")
        
        nendf_desc = (
            "Input Thermal Tape (NENDF).\n"
            "The special ENDF tape containing S(a,b) thermal scattering laws.\n"
            "Example: Tape 24."
        )
        c1.add_input(NjoyInput("nendf", nendf_desc, 24, rule=is_int, is_input_file=True, ref="Page 49"))
        
        nin_desc = (
            "Input PENDF Tape (NIN).\n"
            "The tape containing your current data (usually from BROADR).\n"
            "Standard: 22."
        )
        c1.add_input(NjoyInput("nin", nin_desc, 22, rule=is_int, is_input_file=True, ref="Page 49"))
        
        nout_desc = (
            "Output PENDF Tape (NOUT).\n"
            "The new tape where thermal data will be added.\n"
            "Standard: 23."
        )
        c1.add_input(NjoyInput("nout", nout_desc, 23, rule=is_int, is_output_file=True, ref="Page 49"))
        
        self.add_card(c1, "c1") 

        # --- GUI Control ---
        c_gui = NjoyCard("c_gui", "GUI Setup (This variable does not appear in the final input file)", "Page 49")
        c_gui.add_input(NjoyInput("nmat", "Number of Materials to be processed", current_nmat, rule=is_int, hidden_in_file=True))
        self.add_card(c_gui, "c_gui")

        # --- MATERIAL LOOP ---
        for i in range(1, current_nmat + 1): 
            active_chk = is_mat_active_factory(i)
            
            # --- Card 2: Material Control ---
            c2 = NjoyCard(f"c2_{i}", f"Card 2 (Mat {i}): Config", "Page 49", active_if=active_chk)
            
            matde_desc = (
                "Standard Material ID (MATDE).\n"
                "The ID of the isotope on the PENDF tape (e.g., 1001 for H)."
            )
            c2.add_input(NjoyInput(f"matde_{i}", matde_desc, 1001, rule=is_int, ref="Page 49", options=Data_bases.MAT_DB))

            matdp_desc = (
                "Thermal Material ID (MATDP).\n"
                "The ID of the S(a,b) data on the Thermal Tape.\n"
                "Example: 7 (H in H2O), 11 (H in ZrH).\n"
                "Set to 0 if IIN=1 (Free Gas only)."
            )
            matdp_rule = validate_matdp_consistency_factory(i)
            # ADDED: options=Data_bases.MAT_DB to allow database selection
            c2.add_input(NjoyInput(f"matdp_{i}", matdp_desc, 0, rule=matdp_rule, ref="Page 49", options=Data_bases.MAT_DB))

            nbin_desc = (
                "Number of Energy Bins (NBIN).\n"
                "Number of equi-probable angular bins for incoherent inelastic scattering.\n"
                "Standard: 8 (Good balance of accuracy/size)."
            )
            c2.add_input(NjoyInput(f"nbin_{i}", nbin_desc, 8, rule=is_int, ref="Page 49"))

            ntemp_desc = (
                "Number of Temperatures (NTEMP).\n"
                "How many temperatures to process?\n"
                "Must match the number of temps on the input PENDF."
            )
            c2.add_input(NjoyInput(f"ntemp_{i}", ntemp_desc, 1, rule=is_int, ref="Page 49"))

            iin_desc = (
                "Inelastic Option (IIN).\n"
                "0 = None.\n"
                "1 = Free Gas (No binding effects).\n"
                "2 = S(a,b) (Bound atom, e.g., H in H2O)."
            )
            c2.add_input(NjoyInput(f"iin_{i}", iin_desc, 1, rule=is_int, ref="Page 49"))

            icoh_desc = (
                "Elastic Option (ICOH).\n"
                "0 = None (Liquids like Water).\n"
                "1 = Coherent Elastic (Bragg edges, e.g., Graphite, Be).\n"
                "2 = Incoherent Elastic (Polyethylene, ZrH).\n"
                "10+ = Mixed/Interference options."
            )
            c2.add_input(NjoyInput(f"icoh_{i}", icoh_desc, 0, rule=is_int, ref="Page 49"))

            iform_desc = (
                "Output Format (IFORM).\n"
                "0 = ENDF-6 Standard (Recommended).\n"
                "1 = ACE Format (old style)."
            )
            c2.add_input(NjoyInput(f"iform_{i}", iform_desc, 0, rule=is_int, ref="Page 49"))

            natom_desc = (
                "Number of Atoms (NATOM).\n"
                "0 = Use Principal Atom from ENDF tape (Standard).\n"
                ">0 = Manual definition (Advanced use only)."
            )
            c2.add_input(NjoyInput(f"natom_{i}", natom_desc, 0, rule=is_int, ref="Page 49"))

            mtref_desc = (
                "MT Reference (MTREF).\n"
                "The MT number for the inelastic section.\n"
                "221 = Free Gas.\n"
                "222 = S(a,b) (Standard)."
            )
            c2.add_input(NjoyInput(f"mtref_{i}", mtref_desc, 222, rule=is_int, ref="Page 49"))

            iprint_desc = (
                "Print Option (IPRINT).\n"
                "0 = Minimum.\n"
                "1 = Maximum (Print S(a,b) matrix).\n"
                "2 = Check (Print check results)."
            )
            c2.add_input(NjoyInput(f"iprint_{i}", iprint_desc, 0, rule=is_int, ref="Page 49"))

            self.add_card(c2, f"c2_{i}")

            # --- Card 3: Temperatures ---
            c3 = NjoyCard(f"c3_{i}", f"Card 3 (Mat {i}): Temp List", "Page 49", active_if=active_chk)
            
            tempr_desc = "List of Temperatures (Kelvin). Must match NTEMP count."
            c3.add_input(NjoyInput(f"tempr_{i}", tempr_desc, "293.6", ref="Page 49"))
            
            self.add_card(c3, f"c3_{i}")

            # --- Card 4: Tolerances ---
            c4 = NjoyCard(f"c4_{i}", f"Card 4 (Mat {i}): Limits", "Page 49", active_if=active_chk)
            
            tol_desc = "Tolerance (TOL). Standard: 0.05 (5%)."
            c4.add_input(NjoyInput(f"tol_{i}", tol_desc, 0.05, rule=is_float, ref="Page 49"))
            
            emax_desc = "Max Energy (EMAX) in eV. Standard: 4.0 - 4.5 eV."
            c4.add_input(NjoyInput(f"emax_{i}", emax_desc, 4.5, rule=is_float, ref="Page 49"))
            
            self.add_card(c4, f"c4_{i}")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        lines.append(f"{self.c1.nendf.value} {self.c1.nin.value} {self.c1.nout.value}/")
        
        try: nmat = int(self.c_gui.nmat.value)
        except: nmat = 1
        
        for i in range(1, nmat + 1):
            c2 = getattr(self, f"c2_{i}")
            c3 = getattr(self, f"c3_{i}")
            c4 = getattr(self, f"c4_{i}")
            
            # Card 2
            v2 = [inp.value for inp in c2.inputs]
            lines.append(" ".join(map(str, v2)) + "/")
            
            # Card 3
            raw_temp = str(c3.inputs[0].value)
            lines.append(f"{raw_temp.replace(',', ' ')}/")
            
            # Card 4
            tol = c4.inputs[0].value
            emax = c4.inputs[1].value
            lines.append(f"{tol} {emax}/")


        #thermr does not end with 0/ 
        #lines.append("0 /") 
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nin.value, self.c1.nendf.value]

    @property
    def output_files(self): return [self.c1.nout.value]
from class_def import NjoyCard, NjoyInput
import Data_bases 

class Acer:
    def __init__(self):
        self.name = "acer"
        self.description = """ACER (A Compact ENDF Representation) is the final post-processing module used to generate continuous-energy libraries for Monte Carlo transport codes (MCNP, Serpent).

It ingests the Pointwise-ENDF (PENDF) data—previously processed by RECONR, BROADR, THERMR, and PURR—and transforms it into the specific format required for random sampling.

**Run Modes (IOPT):**
* **1 - Fast Data (.c)**: Standard continuous-energy neutron library. Handles smooth cross-sections, resolved/unresolved resonances, and secondary particle emissions.
* **2 - Thermal Data (.t)**: Thermal scattering laws (S(a,b)) for moderators (e.g., H in H2O, Graphite), handling coherent elastic (Bragg edges) and incoherent inelastic scattering.
* **3 - Dosimetry (.y)**: Generates activation and damage cross-sections.
* **4 - Photoatomic (.p)**: Processes photon interaction data (gamma transport).
* **5 - Photonuclear (.u)**: Processes photonuclear data (gamma-induced neutron production).
* **6 - Consistency Check**: Reads an existing ACE file and performs rigorous internal consistency checks (e.g., probability unitarity, energy grid monotonicity).
* **7 - Print Mode**: Reads an existing ACE file and generates a human-readable printout of its internal tables.

Reference: NJOY2016 Manual, Section 17, Page 499."""
        
        self.ref = "NJOY2016 Manual, Section 17, Page 499"
        self.cards = []
        self.regenerate()

    def regenerate(self):
        # --- Preserve State ---
        current_iopt = 1
        current_nza = 3 # Default minimum is 3
        current_nxtra = 0
        
        if hasattr(self, 'c2'):
            try: current_iopt = int(self.c2.iopt.value)
            except: pass
            try: current_nxtra = int(self.c2.nxtra.value)
            except: pass
            
        if hasattr(self, 'c8_therm'):
            try: 
                val = int(self.c8_therm.nza.value)
                # Constraint: NZA cannot be lower than 3
                current_nza = max(3, val)
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

        def is_0_or_1(x):
            try:
                val = int(x)
                return val == 0 or val == 1
            except: return False

        # --- Visibility Factories ---
        def is_fast(): return int(self.c2.iopt.value) == 1
        def is_thermal(): return int(self.c2.iopt.value) == 2
        def is_dosimetry(): return int(self.c2.iopt.value) == 3
        def is_photoatomic(): return int(self.c2.iopt.value) == 4
        def is_photonuclear(): return int(self.c2.iopt.value) == 5
        
        # Dynamic Visibility for Card 4 (IZ/AW Pairs) based on NXTRA
        def is_iz_aw_active_factory(index):
            return lambda: int(self.c2.nxtra.value) >= index

        # ======================================================================
        # 2. CARD DEFINITIONS
        # ======================================================================

        # --- Card 1: Units ---
        c1 = NjoyCard("c1", "Card 1: I/O Units", "Page 522")
        
        nendf_desc = (
            "Input ENDF Tape (NENDF).\n"
            "The unit number containing the original evaluated data (File 1, 2, 3, etc.).\n"
            "ACER reads atomic masses, Q-values, and resonance parameters directly from this source."
        )
        c1.add_input(NjoyInput("nendf", nendf_desc, 20, rule=is_int, is_input_file=True, ref="Page 522"))
        
        npend_desc = (
            "Input PENDF Tape (NPEND).\n"
            "The unit containing the pointwise processed data (from RECONR/BROADR/THERMR).\n"
            "This tape must contain the linearized, Doppler-broadened cross-sections at the target temperature."
        )
        c1.add_input(NjoyInput("npendf", npend_desc, 21, rule=is_int, is_input_file=True, ref="Page 522"))
        
        ngend_desc = (
            "Input GENDF Tape (NGEND).\n"
            "The unit containing multigroup data. For standard Continuous Energy MCNP libraries (IOPT=1),\n"
            "this is typically not used and should be set to 0 or a dummy unit."
        )
        c1.add_input(NjoyInput("ngend", ngend_desc, 0, rule=is_int, is_input_file=True, ref="Page 522"))
        
        nace_desc = (
            "Output ACE Tape (NACE).\n"
            "The unit number where the final ACE format library file will be written.\n"
            "Note: If IOPT=6 (Check) or IOPT=7 (Print), this unit is treated as the INPUT file to be checked/printed."
        )
        c1.add_input(NjoyInput("nace", nace_desc, 26, rule=is_int, is_output_file=True, ref="Page 522"))
        
        ndir_desc = (
            "Output Directory File (NDIR).\n"
            "The unit number for the 'xsdir' directory snippet.\n"
            "It contains the specific access path, atomic weight, and temperature data required by MCNP configuration."
        )
        c1.add_input(NjoyInput("ndir", ndir_desc, 27, rule=is_int, is_output_file=True, ref="Page 522"))
        self.add_card(c1, "c1")

        # --- Card 2: Control ---
        c2 = NjoyCard("c2", "Card 2: Processing Options", "Page 522")
        
        iopt_desc = (
            "ACE Library Type (IOPT).\n"
            "Controls the physics regime and formatting logic:\n"
            "• 1 = Fast Continuous Energy (.c): Standard neutron transport.\n"
            "• 2 = Thermal Scattering (.t): S(a,b) kernels for moderators.\n"
            "• 3 = Dosimetry (.y): Activation and damage cross-sections.\n"
            "• 4 = Photoatomic (.p): Gamma interaction data.\n"
            "• 5 = Photonuclear (.u): Gamma-induced neutron production.\n"
            "• 6 = Check Mode: Check validity of existing ACE file.\n"
            "• 7 = Print Mode: Print contents of existing ACE file."
        )
        c2.add_input(NjoyInput("iopt", iopt_desc, current_iopt, rule=is_int, ref="Page 522"))
        
        iprint_desc = (
            "Print Verbosity (IPRINT).\n"
            "• 1 = Minimum (Summary only).\n"
            "• 2 = Standard (Recommended). Prints detailed consistency checks, \n"
            "      CDF generation statistics, and results of the energy grid thinning."
        )
        c2.add_input(NjoyInput("iprint", iprint_desc, 2, rule=is_int, ref="Page 522"))
        
        itype_desc = (
            "Output Format (ITYPE).\n"
            "• 1 = ASCII (Type 1). Human-readable and portable (Standard).\n"
            "• 2 = Binary (Type 2). Faster I/O, machine-dependent."
        )
        c2.add_input(NjoyInput("itype", itype_desc, 1, rule=is_int, ref="Page 522"))
        
        suff_desc = (
            "ZAID Suffix (SUFF).\n"
            "The identifier appended to the ZAID in MCNP (e.g., 92235.80c).\n"
            "Enter as decimal: 0.80 becomes '80', 0.70 becomes '70'."
        )
        c2.add_input(NjoyInput("suff", suff_desc, 0.80, rule=is_float, ref="Page 522"))
        
        nxtra_desc = (
            "Material Pairs (NXTRA).\n"
            "Controls the manual definition of materials on Card 4.\n"
            "• 0 = Standard run (Uses first material on tape).\n"
            "• >0 = Number of explicit IZ/AW pairs to define manually."
        )
        c2.add_input(NjoyInput("nxtra", nxtra_desc, current_nxtra, rule=is_int, ref="Page 522"))
        self.add_card(c2, "c2")

        # --- Card 3: Label ---
        c3 = NjoyCard("c3", "Card 3: Library Header", "Page 523")
        hk_desc = (
            "Descriptive Header (HK).\n"
            "A 70-character string describing the source evaluation, temperature, and processing date.\n"
            "This becomes the first line of the ACE file (the ZAID description line)."
        )
        c3.add_input(NjoyInput("hk", hk_desc, "NJOY PROCESSED DATA", ref="Page 523"))
        self.add_card(c3, "c3")

        # --- Card 4: Material (Dynamic IZ/AW pairs) ---
        for i in range(1, 17): 
            c4 = NjoyCard(f"c4_{i}", f"Card 4: Material Pair {i}", "Page 523", active_if=is_iz_aw_active_factory(i))
            
            iz_desc = f"Material ZAID (IZ_{i}). The NJOY/ENDF MAT number of the target isotope."
            c4.add_input(NjoyInput(f"iz_{i}", iz_desc, 125, rule=is_int, options=Data_bases.MAT_DB, ref="Page 523"))
            
            aw_desc = f"Atomic Weight Ratio (AW_{i}). Set to 0.0 for auto-detection."
            c4.add_input(NjoyInput(f"aw_{i}", aw_desc, 0.0, rule=is_float, ref="Page 523"))
            self.add_card(c4, f"c4_{i}")

        # Note: If IOPT = 6 or 7, logic stops here.
        
        # ======================================================================
        # FAST DATA (IOPT=1)
        # ======================================================================
        c5 = NjoyCard("c5_fast", "Card 5 (Fast): Configuration", "Page 523", active_if=is_fast)
        c5.add_input(NjoyInput("matd", "Processing Material ID (MATD)", 125, rule=is_int, ref="Page 523"))
        c5.add_input(NjoyInput("tempd", "Temperature (TEMPD)", 293.6, rule=is_float, ref="Page 523"))
        self.add_card(c5, "c5_fast")

        c6 = NjoyCard("c6_fast", "Card 6 (Fast): Physics Flags", "Page 523", active_if=is_fast)
        c6.add_input(NjoyInput("newfor", "Energy-Angle Dist (1=Law 61)", 1, rule=is_int, ref="Page 523"))
        c6.add_input(NjoyInput("iopp", "Photon Production (1=Detailed)", 1, rule=is_int, ref="Page 523"))
        c6.add_input(NjoyInput("ismooth", "Spectrum Smoothing (1=Yes)", 1, rule=is_int, ref="Page 523"))
        self.add_card(c6, "c6_fast")

        c7_fast_gui = NjoyCard("c7_fast_gui", "Card 7 (Fast GUI Helper)", "Page 523", active_if=is_fast)
        c7_fast_gui.add_input(NjoyInput("thinning", "1 = Thinning Enabled, 0 = Disabled", 0, rule=is_0_or_1))

        self.add_card(c7_fast_gui, "c7_fast_gui")

        if int(c7_fast_gui.thinning.value) == 1:

            c7 = NjoyCard("c7_fast", "Card 7 (Fast): Grid Thinning", "Page 523", active_if=is_fast)
            c7.add_input(NjoyInput("thin1", "Reconstruction Tolerance (0.005=Std)", 0.005, rule=is_float, ref="Page 523"))
            c7.add_input(NjoyInput("thin2", "Thinning Threshold (eV)", "1.0e6", rule=is_float, ref="Page 523"))
            c7.add_input(NjoyInput("thin3", "Thinning Type (2=Integral)", 2, rule=is_int, ref="Page 523"))
            self.add_card(c7, "c7_fast")

        # ======================================================================
        # THERMAL DATA (IOPT=2)
        # ======================================================================
        
        # --- Card 8 (Thermal) ---
        c8 = NjoyCard("c8_therm", "Card 8 (Therm): Configuration", "Page 528", active_if=is_thermal)
        c8.add_input(NjoyInput("matd", "Processing Material ID (MATD)", 0, rule=is_int, ref="Page 528", options=Data_bases.MAT_DB))
        c8.add_input(NjoyInput("tempd", "Temperature (TEMPD)", 293.6, rule=is_float, ref="Page 528"))
        c8.add_input(NjoyInput("tname", "Thermal Name (e.g. lwtr)", "lwtr", ref="Page 528"))
        
        nza_desc = (
            "Number of Principal Atoms (NZA).\n"
            "Number of distinct isotopes mixed in this thermal file (Min 3).\n"
            "If NZA > 1, it defines a mixed moderator."
        )
        # Enforce minimum NZA of 3
        c8.add_input(NjoyInput("nza", nza_desc, current_nza, rule=is_int, ref="Page 528"))
        self.add_card(c8, "c8_therm")

        # --- Card 8a (Thermal): Dynamic Atom List ---
        c8a = NjoyCard("c8a_therm", "Card 8a: Moderator Atoms List", "Page 528", active_if=is_thermal)
        
        # Dynamically create iza_1, iza_2, ... iza_NZA
        for i in range(1, current_nza + 1):
            iza_desc = (
                f"Moderator ZA (IZA_{i}).\n"
                "The ZAID of the principal scatterer (e.g., 1001 for H, 600 for C).\n"
                "These link the thermal scattering law to specific isotope transport cross-sections."
            )
            c8a.add_input(NjoyInput(f"iza_{i}", iza_desc, 0, rule=is_int, ref="Page 528"))
            
        self.add_card(c8a, "c8a_therm")

        # --- Card 9 (Thermal) ---
        c9 = NjoyCard("c9_therm", "Card 9 (Therm): Physics Flags", "Page 528", active_if=is_thermal)
        c9.add_input(NjoyInput("mti", "Inelastic Reaction MT (222=Std)", 222, rule=is_int, ref="Page 528"))
        c9.add_input(NjoyInput("nbint", "Number of Angular Bins (Std=8)", 8, rule=is_int, ref="Page 528"))
        c9.add_input(NjoyInput("mtem", "Config Energies (MTEM)", 1, rule=is_int, ref="Page 528"))
        c9.add_input(NjoyInput("ielas", "Elastic MT (0=None, 230+=Solid)", 0, rule=is_int, ref="Page 528"))
        c9.add_input(NjoyInput("nmix", "Atom Count (NMIX)", 1, rule=is_int, ref="Page 528"))
        c9.add_input(NjoyInput("emax", "Max Thermal Energy (eV)", 4.0, rule=is_float, ref="Page 528"))
        c9.add_input(NjoyInput("iwt", "Weighting (0=Const)", 0, rule=is_int, ref="Page 528"))
        self.add_card(c9, "c9_therm")

        # ======================================================================
        # OTHER MODES (3, 4, 5)
        # ======================================================================
        c10 = NjoyCard("c10_dos", "Card 10: Dosimetry Config", "Page 530", active_if=is_dosimetry)
        c10.add_input(NjoyInput("matd", "Material ID (MATD)", 0, rule=is_int, ref="Page 530"))
        c10.add_input(NjoyInput("tempd", "Temperature (TEMPD)", 300.0, rule=is_float, ref="Page 530"))
        self.add_card(c10, "c10_dos")

        c11 = NjoyCard("c11_photo", "Card 11: Photoatomic Config", "Page 530", active_if=is_photoatomic)
        c11.add_input(NjoyInput("matd", "Material ID (MATD). Use Z*1000.", 0, rule=is_int, ref="Page 530"))
        self.add_card(c11, "c11_photo")

        c12 = NjoyCard("c12_pnuc", "Card 12: Photonuclear Config", "Page 530", active_if=is_photonuclear)
        c12.add_input(NjoyInput("matd", "Material ID (MATD)", 0, rule=is_int, ref="Page 530"))
        self.add_card(c12, "c12_pnuc")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        
        # --- Card 1 ---
        c1 = self.c1
        lines.append(f"{c1.nendf.value} {c1.npendf.value} {c1.ngend.value} {c1.nace.value} {c1.ndir.value}/")
        
        # --- Card 2 ---
        c2 = self.c2
        iopt = int(c2.iopt.value)
        try: nxtra = int(c2.nxtra.value)
        except: nxtra = 0
        
        lines.append(f"{c2.iopt.value} {c2.iprint.value} {c2.itype.value} {c2.suff.value} {c2.nxtra.value}/")
        
        # --- Card 3 ---
        hk = str(self.c3.hk.value).strip("'\"")
        lines.append(f"'{hk}'/")
        
        # --- Card 4 (Dynamic IZ/AW Pairs) ---
        if nxtra > 0:
            for i in range(1, nxtra + 1):
                if hasattr(self, f"c4_{i}"):
                    card = getattr(self, f"c4_{i}")
                    iz = card.inputs[0].value
                    aw = card.inputs[1].value
                    lines.append(f"{iz} {aw}/")
        
        # --- BRANCHES ---
        if iopt == 1: # Fast
            c5, c6, c7 = self.c5_fast, self.c6_fast, self.c7_fast
            c7_fast_gui = self.c7_fast_gui
            lines.append(f"{c5.matd.value} {c5.tempd.value}/")
            lines.append(f"{c6.newfor.value} {c6.iopp.value} {c6.ismooth.value}/")
            if c7_fast_gui.thinning.value == '1':
                lines.append(f"{c7.thin1.value} {c7.thin2.value} {c7.thin3.value}/")
            
        elif iopt == 2: # Thermal
            c8, c9 = self.c8_therm, self.c9_therm
            tname = str(c8.tname.value).strip("'\"")
            lines.append(f"{c8.matd.value} {c8.tempd.value} '{tname}' {c8.nza.value}/")
            
            # Dynamic IZAs from c8a_therm
            # Collect iza_1, iza_2 ... iza_NZA
            try: nza = int(c8.nza.value)
            except: nza = 3
            nza = max(3, nza)
            
            iza_list = []
            for i in range(1, nza + 1):
                try:
                    val = getattr(self.c8a_therm, f"iza_{i}").value
                    iza_list.append(str(val))
                except AttributeError:
                    iza_list.append("0")

            lines.append(" ".join(iza_list) + "/")
            
            lines.append(f"{c9.mti.value} {c9.nbint.value} {c9.mtem.value} {c9.ielas.value} {c9.nmix.value} {c9.emax.value} {c9.iwt.value}/")
            
        elif iopt == 3: # Dosimetry
            lines.append(f"{self.c10_dos.matd.value} {self.c10_dos.tempd.value}/")
            
        elif iopt == 4: # Photoatomic
            lines.append(f"{self.c11_photo.matd.value}/")
            
        elif iopt == 5: # Photonuclear
            lines.append(f"{self.c12_pnuc.matd.value}/")

        # IOPT 6 (Check) and 7 (Print) do not write any additional cards.

        #acer does not finish with 0/ 
        #lines.append("0/") 
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nendf.value, self.c1.npendf.value]
    @property
    def output_files(self): return [self.c1.nace.value, self.c1.ndir.value]
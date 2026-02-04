from class_def import NjoyCard, NjoyInput
import Data_bases

class Purr:
    def __init__(self):
        self.name = "purr"
        self.description = (
            "PURR generates probability tables for the Unresolved Resonance Region.\n"
            "These tables allow continuous-energy Monte Carlo codes (like MCNP) to \n"
            "account for self-shielding effects where resonances are too close to be \n"
            "resolved individually.\n\n"
            "It computes the probability distribution of cross-sections by generating \n"
            "random 'ladders' of resonances based on average parameters."
        )
        self.ref = "NJOY2016 Manual, Section 23, Page 635"
        self.cards = []
        self.regenerate()

    def regenerate(self):
        self.cards = []

        # --- Logic Helpers ---
        def is_int(x):
            try: return int(x) or True
            except: return False
        
        def is_float(x):
            try: 
                val = str(x).lower().replace('d', 'e')
                return float(val) or True
            except: return False

        def validate_temp_count(value):
            try:
                # Must match ntemp on Card 2
                count = int(self.c2.ntemp.value)
                values = str(value).replace(",", " ").split()
                return len(values) == count
            except: return False

        def validate_sigz_count(value):
            try:
                # Must match nsigz on Card 2
                count = int(self.c2.nsigz.value)
                values = str(value).replace(",", " ").split()
                return len(values) == count
            except: return False

        # --- Card 1: I/O Units ---
        c1 = NjoyCard("c1", "Card 1: I/O Units", "Page 642")
        
        nendf_desc = (
            "Input ENDF Tape (NENDF).\n"
            "The unit number for the original ENDF tape. Used to read the unresolved \n"
            "resonance parameters (File 2)."
        )
        c1.add_input(NjoyInput("nendf", nendf_desc, 20, rule=is_int, is_input_file=True, ref="Page 642"))

        nin_desc = (
            "Input PENDF Tape (NIN).\n"
            "The unit number for the input PENDF tape (from RECONR/BROADR/HEATR).\n"
            "Must contain the smooth cross-sections."
        )
        c1.add_input(NjoyInput("nin", nin_desc, 21, rule=is_int, is_input_file=True, ref="Page 642"))

        nout_desc = (
            "Output PENDF Tape (NOUT).\n"
            "The unit number for the output PENDF tape.\n"
            "This will contain the original data plus the new probability tables (MF=2, MT=153)."
        )
        c1.add_input(NjoyInput("nout", nout_desc, 22, rule=is_int, is_output_file=True, ref="Page 642"))
        self.add_card(c1, "c1")

        # --- Card 2: Control Parameters ---
        c2 = NjoyCard("c2", "Card 2: Processing Options", "Page 642")

        matd_desc = (
            "Material ID (MATD).\n"
            "The ENDF material number to process (e.g., 9228 for U-235).\n"
            "Must match the material on the input tapes."
        )
        c2.add_input(NjoyInput("matd", matd_desc, 125, rule=is_int, options=Data_bases.MAT_DB, ref="Page 642"))

        ntemp_desc = (
            "Number of Temperatures (NTEMP).\n"
            "How many temperatures to process. Must match the number of temperatures\n"
            "already present on the input PENDF tape."
        )
        c2.add_input(NjoyInput("ntemp", ntemp_desc, 1, rule=is_int, ref="Page 642"))

        nsigz_desc = (
            "Number of Sigma Zeros (NSIGZ).\n"
            "Number of background cross-section values for self-shielding calculations.\n"
            "Default: 1 (Infinity only)."
        )
        c2.add_input(NjoyInput("nsigz", nsigz_desc, 1, rule=is_int, ref="Page 642"))

        nbin_desc = (
            "Number of Probability Bins (NBIN).\n"
            "The number of bins in the probability table.\n"
            "Common choice: 20."
        )
        c2.add_input(NjoyInput("nbin", nbin_desc, 20, rule=is_int, ref="Page 642"))

        nladr_desc = (
            "Number of Ladders (NLADR).\n"
            "The number of random resonance ladders to generate for statistics.\n"
            "Higher numbers give better accuracy but take longer.\n"
            "Recommended: 32 or 64."
        )
        c2.add_input(NjoyInput("nladr", nladr_desc, 32, rule=is_int, ref="Page 642"))

        iprint_desc = (
            "Print Option (IPRINT).\n"
            "0 = Minimum printing.\n"
            "1 = Maximum printing (shows tables)."
        )
        c2.add_input(NjoyInput("iprint", iprint_desc, 1, rule=is_int, ref="Page 642"))

        nunx_desc = (
            "Number of Energy Points (NUNX).\n"
            "Number of unresolved energy points to process.\n"
            "0 = Process all points (Standard).\n"
            ">0 = Debugging option to limit run."
        )
        c2.add_input(NjoyInput("nunx", nunx_desc, 0, rule=is_int, ref="Page 642"))
        self.add_card(c2, "c2")

        # --- Card 3: Temperatures ---
        c3 = NjoyCard("c3", "Card 3: Temperature List", "Page 642")
        temp_desc = (
            "Temperatures (TEMP).\n"
            "List of temperatures in Kelvin. Must match the input PENDF tape."
        )
        c3.add_input(NjoyInput("temp", temp_desc, "293.6", rule=validate_temp_count, ref="Page 642"))
        self.add_card(c3, "c3")

        # --- Card 4: Sigma Zeros ---
        c4 = NjoyCard("c4", "Card 4: Background Cross Sections", "Page 642")
        sigz_desc = (
            "Sigma Zero Values (SIGZ).\n"
            "List of background cross-sections for self-shielding.\n"
            "Include 1.0E10 (infinity) as the first value.\n"
            "Example: 1.0E10 1000. 100. 10."
        )
        c4.add_input(NjoyInput("sigz", sigz_desc, "1.0E10", rule=validate_sigz_count, ref="Page 642"))
        self.add_card(c4, "c4")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        
        # Card 1
        lines.append(f"{self.c1.nendf.value} {self.c1.nin.value} {self.c1.nout.value}/")
        
        # Card 2
        c2 = self.c2
        lines.append(f"{c2.matd.value} {c2.ntemp.value} {c2.nsigz.value} "
                     f"{c2.nbin.value} {c2.nladr.value} {c2.iprint.value} {c2.nunx.value}/")
        
        # Card 3 (Temperatures)
        lines.append(f"{self.c3.temp.value}/")
        
        # Card 4 (Sigmas)
        lines.append(f"{self.c4.sigz.value}/")
        lines.append("0/")  # End of PURR input
        
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nin.value]
    @property
    def output_files(self): return [self.c1.nout.value]
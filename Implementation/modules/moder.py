from class_def import NjoyCard, NjoyInput
import Data_bases 

# ==============================================================================
# 2. MODULE DEFINITIONS
# ==============================================================================
class Moder:
    def __init__(self):
        self.name = "moder"
        self.description = (
            "MODER (Mode Conversion) is often the first or last step in an NJOY run.\n"
            "Its main job is to convert ENDF 'Tapes' (files) between two formats:\n"
            "1. ASCII (Coded): Human-readable text files. Good for viewing/editing.\n"
            "2. Binary (Blocked): Computer-readable binary files. Faster, smaller, and standard for NJOY processing.\n\n"
            "It can also 'Selectively Copy' specific materials from one tape to another."
        )
        self.ref = "NJOY2016 Manual, Section 3, Page 28"
        self.cards = []

        # ======================================================================
        # 1. LOGIC HELPERS
        # ======================================================================
        def is_int(x):
            try: return int(x) or True
            except: return False

        def is_selective():
            """Active if nin is between +/- 1 and 19."""
            try: return 1 <= abs(int(self.c1.nin.value)) <= 19
            except: return False

        def get_nmats():
            """Get number of materials to process (from Card 2 input)."""
            try: return max(1, int(self.c2.num_mats.value))
            except: return 1

        def is_mat_active_factory(index):
            """Show Card 3_i only if we are in selective mode AND index <= requested count."""
            return lambda: is_selective() and index <= get_nmats()

        def format_tpid():
            try:
                s = str(self.c2.tpid.value).strip()[:66]
                if not (s.startswith("'") and s.endswith("'")): return f"'{s}'"
                return s
            except: return "'NJOY TAPE'"

        # ======================================================================
        # 2. CARD DEFINITIONS
        # ======================================================================
        
        # --- Card 1: Configuration ---
        c1 = NjoyCard("c1", "I/O Configuration", "Page 28")
        
        nin_desc = (
            "Input Unit (NIN).\n"
            "Specifies the input tape number and the operation mode:\n"
            " • 20 to 99: Converts Binary input -> ASCII output.\n"
            " • -20 to -99: Converts ASCII input -> Binary output (Standard use).\n"
            " • 1 to 19 (or -1 to -19): 'Selective Copy' mode. Allows you to extract specific materials.\n" \
            " • nin = 1 for endf or pendf input and output." \
            " • nin = 2 for gendf input and output." \
            " • nin = 3 for errorr-format input and output. "
        )

        nout_desc = (
            "Output Unit (NOUT).\n"
            "Specifies the tape number for the result file.\n"
            " • Positive (e.g., 21): Writes a Binary file.\n"
            " • Negative (e.g., -21): Writes an ASCII file."
        )

        c1.add_input(NjoyInput("nin", nin_desc, 20, rule=is_int, is_input_file=True, ref="Page 28"))
        c1.add_input(NjoyInput("nout", nout_desc, 21, rule=is_int, is_output_file=True, ref="Page 28"))
        
        self.add_card(c1)

        # --- Card 2: Label & Control ---
        c2 = NjoyCard("c2", "Output Tape Label", "Page 29", active_if=is_selective)
        
        tpid_desc = (
            "Tape Label (TPID).\n"
            "A title for the new output tape (max 66 chars).\n"
            "Since you are creating a new custom tape, give it a descriptive name.\n"
            "Example: 'U-235 and Pu-239 for Project X'."
        )
        tpid = c2.add_input(NjoyInput("tpid", tpid_desc, "NJOY TAPE", ref="Page 29"))
        tpid.get_string_value = format_tpid 

        # GUI ONLY Input (Hidden in file)
        num_mats_desc = (
            "Number of Materials to Copy (GUI Only).\n"
            "How many different materials do you want to extract from the source tape?\n"
            "Increasing this number adds more rows below."
        )
        c2.add_input(NjoyInput("num_mats", num_mats_desc, 1, rule=is_int, hidden_in_file=True))

        self.add_card(c2)

        # --- Card 3 Loop: Material Selection ---
        # Generate slots for up to 10 materials
        for i in range(1, 11):
            active_chk = is_mat_active_factory(i)
            
            c3 = NjoyCard(f"c3_{i}", f"Material Copy #{i}", "Page 29", active_if=active_chk)
            
            nin_i_desc = (
                "Source Input Unit.\n"
                "The unit number of the tape containing the material you want.\n"
                "This allows you to merge materials from different files into one output."
            )
            c3.add_input(NjoyInput(f"nin_{i}", nin_i_desc, 20, rule=is_int, is_input_file=True, ref="Page 29"))
            
            matd_i_desc = (
                "Material ID (MATD).\n"
                "The specific integer ID of the isotope to copy (e.g., 9228 for U-235).\n"
                "Use the 'Select' button (≡) to find IDs."
            )
            c3.add_input(NjoyInput(f"matd_{i}", matd_i_desc, 125, rule=is_int, ref="Page 29", options=Data_bases.MAT_DB))
            
            self.add_card(c3)

    def add_card(self, card: NjoyCard):
        self.cards.append(card)
        setattr(self, card.name, card)
        return card

    def write(self):
        lines = [self.name]
        
        # 1. Write Standard Cards
        for card in self.cards:
            text = card.write()
            if text: lines.append(text)
        
        # 2. Handle Termination for Selective Mode
        # If in selective mode (abs(nin) 1-19), we must end the material list with a 0/
        if 1 <= abs(int(self.c1.nin.value)) <= 19:
            lines.append("0/") 

        return "\n".join(lines)

    @property
    def input_files(self):
        return [self.c1.nin.value]

    @property
    def output_files(self):
        return [self.c1.nout.value]
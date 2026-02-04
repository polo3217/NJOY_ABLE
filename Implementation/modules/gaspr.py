from class_def import NjoyCard, NjoyInput
import Data_bases

class Gaspr:
    def __init__(self):
        self.name = "gaspr"
        self.description = (
            "GASPR calculates gas-production cross sections.\n"
            "It scans the PENDF file for reactions that produce light particles \n"
            "(p, d, t, He-3, alpha) and sums them up to create new reaction sections:\n"
            "  MT=203 (Total H production)\n"
            "  MT=204 (Total D production)\n"
            "  MT=205 (Total T production)\n"
            "  MT=206 (Total He-3 production)\n"
            "  MT=207 (Total He-4 production)\n"
            "This is useful for radiation damage and embrittlement studies."
        )
        self.ref = "NJOY2016 Manual, Section 25, Page 723"
        self.cards = []
        self.regenerate()

    def regenerate(self):
        self.cards = []

        # --- Logic Helpers ---
        def is_int(x):
            try: return int(x) or True
            except: return False

        # --- Card 1: I/O Units ---
        c1 = NjoyCard("c1", "Card 1: I/O Units", "Page 724")
        
        nendf_desc = (
            "Input ENDF Tape (NENDF).\n"
            "The unit number for the original ENDF tape.\n"
            "Used to check for File 6 gas production data."
        )
        c1.add_input(NjoyInput("nendf", nendf_desc, 20, rule=is_int, is_input_file=True, ref="Page 724"))

        nin_desc = (
            "Input PENDF Tape (NIN).\n"
            "The unit number for the input PENDF tape.\n"
            "This should contain the pointwise cross sections (e.g., from BROADR)."
        )
        c1.add_input(NjoyInput("nin", nin_desc, 21, rule=is_int, is_input_file=True, ref="Page 724"))

        nout_desc = (
            "Output PENDF Tape (NOUT).\n"
            "The unit number for the output PENDF tape.\n"
            "It will be a copy of NIN with the new gas production MTs (203-207) added."
        )
        c1.add_input(NjoyInput("nout", nout_desc, 22, rule=is_int, is_output_file=True, ref="Page 724"))
        self.add_card(c1, "c1") 

        # Note: GASPR does not have a Card 2 for Material selection. 
        # It automatically processes the first material found on the tape.
        # Users should ensure the tape contains only the desired material 
        # (e.g., by using MODER before this step).

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        lines.append(f"{self.c1.nendf.value} {self.c1.nin.value} {self.c1.nout.value}/")
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nin.value]
    @property
    def output_files(self): return [self.c1.nout.value]
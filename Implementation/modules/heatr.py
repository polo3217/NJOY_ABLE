from class_def import NjoyCard, NjoyInput
import Data_bases
# ==============================================================================
# 16. HEATR (Heating & Damage) - Manual Section 16
# ==============================================================================
class Heatr:
    def __init__(self):
        self.name = "heatr"
        self.description = "HEATR computes heat production (KERMA) and radiation damage (DPA) cross-sections."
        self.ref = "NJOY2016 Manual, Section 16, Page 225"
        self.cards = []
        
        def is_int(x): return int(x) or True
        
        # C1
        c1 = NjoyCard("c1", "I/O Units", "Page 225")
        c1.add_input(NjoyInput("nendf", "Input ENDF", 20, rule=is_int, is_input_file=True))
        c1.add_input(NjoyInput("nin", "Input PENDF", 22, rule=is_int, is_input_file=True))
        c1.add_input(NjoyInput("nout", "Output PENDF (with heating)", 24, rule=is_int, is_output_file=True))
        self.add_card(c1, "c1")
        
        # C2 - Mat loop
        c2 = NjoyCard("c2", "Material Control", "Page 225")
        c2.add_input(NjoyInput("matd", "Material ID", 125, rule=is_int, options=Data_bases.MAT_DB))
        c2.add_input(NjoyInput("npk", "Num. Partial Kermas (usually 0)", 0, rule=is_int))
        c2.add_input(NjoyInput("nqa", "Num. User Q-Values (usually 0)", 0, rule=is_int))
        c2.add_input(NjoyInput("ntemp", "Num. Temperatures (0=All)", 0, rule=is_int))
        c2.add_input(NjoyInput("local", "Local Deposition? (0=No, 1=Yes)", 0, rule=is_int))
        c2.add_input(NjoyInput("iprint", "Print Check? (0=No, 1=Yes)", 0, rule=is_int))
        self.add_card(c2, "c2")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        lines.append(f"{self.c1.nendf.value} {self.c1.nin.value} {self.c1.nout.value}/")
        
        # Simple single material logic for now
        lines.append(f"{self.c2.matd.value} {self.c2.npk.value} {self.c2.nqa.value} "
                     f"{self.c2.ntemp.value} {self.c2.local.value} {self.c2.iprint.value}/")
        lines.append("0/")
        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nin.value]
    @property
    def output_files(self): return [self.c1.nout.value]
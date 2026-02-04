from class_def import NjoyCard, NjoyInput
import Data_bases
# ==============================================================================
# 7. UNRESR (Unresolved Resonance Self-Shielding) - Manual Section 7
# ==============================================================================
class Unresr:
    def __init__(self):
        self.name = "unresr"
        self.description = (
            "UNRESR calculates self-shielded effective cross-sections in the 'Unresolved' resonance region.\n"
            "This is crucial for fast reactors where neutrons have high energy."
        )
        self.ref = "NJOY2016 Manual, Section 7, Page 67"
        self.cards = []
        
        def is_int(x): return int(x) or True

        # C1
        c1 = NjoyCard("c1", "I/O Units", "Page 67")
        c1.add_input(NjoyInput("nendf", "Input ENDF", 20, rule=is_int, is_input_file=True))
        c1.add_input(NjoyInput("nin", "Input PENDF", 22, rule=is_int, is_input_file=True))
        c1.add_input(NjoyInput("nout", "Output PENDF", 23, rule=is_int, is_output_file=True))
        self.add_card(c1, "c1")
        
        # C2
        c2 = NjoyCard("c2", "Material", "Page 67")
        c2.add_input(NjoyInput("matd", "Material ID", 125, rule=is_int, options=Data_bases.MAT_DB))
        c2.add_input(NjoyInput("ntemp", "Number of Temperatures", 1, rule=is_int))
        c2.add_input(NjoyInput("nsigz", "Number of Sigma-Zeros", 1, rule=is_int))
        c2.add_input(NjoyInput("nprint", "Print Option (1=Standard)", 1, rule=is_int))
        self.add_card(c2, "c2")

        # C3: Temps
        c3 = NjoyCard("c3", "Temperatures", "Page 67")
        c3.add_input(NjoyInput("temp", "Temperature List (K)", "293.6"))
        self.add_card(c3, "c3")

        # C4: Sigmas
        c4 = NjoyCard("c4", "Sigma Zeros", "Page 67")
        c4.add_input(NjoyInput("sigz", "Sigma Zero List", "1.0e10"))
        self.add_card(c4, "c4")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        lines.append(f"{self.c1.nendf.value} {self.c1.nin.value} {self.c1.nout.value}/")
        lines.append(f"{self.c2.matd.value} {self.c2.ntemp.value} {self.c2.nsigz.value} {self.c2.nprint.value}/")
        lines.append(f"{str(self.c3.temp.value).replace(',', ' ')}/")
        lines.append(f"{str(self.c4.sigz.value).replace(',', ' ')}/")
        lines.append("0/")
        return "\n".join(lines)
    
    @property
    def input_files(self): return [self.c1.nin.value]
    @property
    def output_files(self): return [self.c1.nout.value]
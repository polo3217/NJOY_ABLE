from class_def import NjoyCard, NjoyInput
import Data_bases
# ==============================================================================
# 18. PLOTR (Plotting) - Manual Section 18
# ==============================================================================
class Plotr:
    def __init__(self):
        self.name = "plotr"
        self.description = "PLOTR generates plots of cross sections and other data from ENDF/PENDF/GENDF tapes."
        self.ref = "NJOY2016 Manual, Section 18, Page 273"
        self.cards = []

        def is_int(x): return int(x) or True

        c1 = NjoyCard("c1", "I/O Units", "Page 273")
        c1.add_input(NjoyInput("lorig", "Input Data Unit (e.g. PENDF)", 21, rule=is_int, is_input_file=True))
        c1.add_input(NjoyInput("lplot", "Output Plot File", 26, rule=is_int, is_output_file=True))
        self.add_card(c1, "c1")
        
        c2 = NjoyCard("c2", "General Plot Config", "Page 273")
        # Simplified for general users
        c2.add_input(NjoyInput("itype", "Plot Type (1=LogLog, 2=LogLin...)", 1, rule=is_int))
        self.add_card(c2, "c2")

        c3 = NjoyCard("c3", "Curve 1", "Page 274")
        c3.add_input(NjoyInput("mat", "Material ID", 125, rule=is_int, options=Data_bases.MAT_DB))
        c3.add_input(NjoyInput("mf", "File (MF) (3=Sigma)", 3, rule=is_int))
        c3.add_input(NjoyInput("mt", "Reaction (MT)", 1, rule=is_int, options=Data_bases.MT_DB))
        c3.add_input(NjoyInput("temp", "Temperature", 293.6))
        self.add_card(c3, "c3")

        c4 = NjoyCard("c4", "Title", "Page 275")
        c4.add_input(NjoyInput("title", "Plot Title", "CROSS SECTION"))
        self.add_card(c4, "c4")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        lines.append(f"0 {self.c1.lorig.value} {self.c1.lplot.value}/")
        
        # Simple plot: 1 curve
        lines.append(f"{self.c2.itype.value}/")
        lines.append(f"{self.c3.mat.value} {self.c3.mf.value} {self.c3.mt.value} {self.c3.temp.value}/")
        
        title = self.c4.title.value
        if not (title.startswith("'") and title.endswith("'")): title = f"'{title}'"
        lines.append(f"{title}/")
        
        lines.append("0/") # Terminate
        return "\n".join(lines)
    
    @property
    def input_files(self): return [self.c1.lorig.value]
    @property
    def output_files(self): return [self.c1.lplot.value]
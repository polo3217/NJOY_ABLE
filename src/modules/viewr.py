from class_def import NjoyCard, NjoyInput
import Data_bases
# ==============================================================================
# 19. VIEWR (Plot Rendering) - Manual Section 19
# ==============================================================================
class Viewr:
    def __init__(self):
        self.name = "viewr"
        self.description = "VIEWR converts the raw plot commands from PLOTR into a Viewable format (PostScript/EPS)."
        self.ref = "NJOY2016 Manual, Section 19, Page 303"
        self.cards = []

        def is_int(x): return int(x) or True

        c1 = NjoyCard("c1", "I/O Units", "Page 303")
        c1.add_input(NjoyInput("nplot", "Input Plot File (from PLOTR)", 26, rule=is_int, is_input_file=True))
        c1.add_input(NjoyInput("nps", "Output PostScript File", 50, rule=is_int, is_output_file=True))
        self.add_card(c1, "c1")
        
  

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        lines.append(f"{self.c1.nplot.value} {self.c1.nps.value}/")
        return "\n".join(lines)
    
    @property
    def input_files(self): return [self.c1.nplot.value]
    @property
    def output_files(self): return [self.c1.nps.value]
from typing import List, Callable, Optional, Union

# ==============================================================================
# 1. CORE LOGIC CLASSES
# ==============================================================================
class NjoyInput:
    def __init__(self, name: str, description: str = "", default_value: any = None, 
                 rule: Callable[[any], bool] = lambda x: True, ref: str = "",
                 is_input_file: bool = False, is_output_file: bool = False,
                 options: dict = None, 
                 hidden_in_file: bool = False):  # <--- NEW PARAMETER
        self.name = name
        self.description = description
        self.value = default_value 
        self.rule = rule            
        self.ref = ref              
        self.is_input_file = is_input_file
        self.is_output_file = is_output_file
        self.options = options
        self.hidden_in_file = hidden_in_file     # <--- STORE IT
        self.status = True       

    def validate(self) -> bool:
        try:
            if not self.rule(self.value):
                self.status = False
            else:
                self.status = True
        except Exception:
            self.status = False
        return self.status

    def get_string_value(self) -> str:
        if self.value is None: return ""
        return str(self.value)

class NjoyCard:
    def __init__(self, name: str, description: str = "", ref: str = "", active_if=None):
        self.name = name
        self.description = description
        self.ref = ref
        self.inputs: List[NjoyInput] = [] 
        self.active_if = active_if

    def add_input(self, inp: NjoyInput):
        self.inputs.append(inp)
        setattr(self, inp.name, inp)
        return inp 

    def write(self) -> Optional[str]:
            # 1. Check if the whole card is active
            if self.active_if and not self.active_if(): 
                return None 
            
            # 2. Collect values ONLY for inputs that are NOT hidden
            values = []
            for inp in self.inputs:
                if not inp.hidden_in_file:  # <--- FILTER HERE
                    values.append(inp.get_string_value())
            
            return " ".join(values) +"/"
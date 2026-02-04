from class_def import NjoyCard, NjoyInput
import Data_bases 

class Errorr:
    def __init__(self):
        self.name = "errorr"
        self.description = (
            "ERRORR processes covariance data from ENDF files (File 31, 33, 34, 35, 40) into multigroup format.\n"
            "It computes the covariance matrices of multigroup cross-sections, which quantify the uncertainties "
            "and correlations in the nuclear data.\n\n"
            "Key capabilities include:\n"
            "- Processing resonance parameter covariances (MF32) into group constants.\n"
            "- Combining uncertainties from different reaction channels.\n"
            "- Handling ratio-to-standard covariance data.\n\n"
            "Reference: NJOY2016 Manual, Section 10, Page 129 & 317."
        )
        self.ref = "NJOY2016 Manual, Section 10, Page 317"
        self.cards = []
        self.regenerate()

    def regenerate(self):
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

        # --- Visibility Factories ---
        def is_ign_user_defined():
            try: return int(self.c2.ign.value) in [1, 19]
            except: return False

        def is_iwt_tabulated():
            try: return int(self.c2.iwt.value) == 1
            except: return False

        def is_iwt_analytic():
            try: return int(self.c2.iwt.value) == 4
            except: return False

        def is_iread_1():
            try: return int(self.c7.iread.value) == 1
            except: return False

        def is_iread_2():
            try: return int(self.c7.iread.value) == 2
            except: return False
            
        def is_nek_nonzero():
            try: return int(self.c8.nek.value) > 0
            except: return False

        def is_nstan_nonzero():
            try: return int(self.c1.nstan.value) != 0
            except: return False

        # ======================================================================
        # 2. CARD DEFINITIONS
        # ======================================================================

        # --- Card 1: Units ---
        c1 = NjoyCard("c1", "Card 1: I/O Units", "Page 317")
        c1.add_input(NjoyInput("nendf", "Input ENDF Tape (NENDF).\nUnit for original evaluated data (File 1, 2, 31-40).", 20, rule=is_int, is_input_file=True, ref="Page 317"))
        c1.add_input(NjoyInput("npend", "Input PENDF Tape (NPEND).\nUnit for pointwise cross-sections from RECONR/BROADR.", 21, rule=is_int, is_input_file=True, ref="Page 317"))
        c1.add_input(NjoyInput("ngout", "Input GENDF Tape (NGOUT).\nIf 0, group xsecs are calculated internally.\nMust be set if IREAD=2 or MFCOV=35 to read existing group data.", 0, rule=is_int, is_input_file=True, ref="Page 317"))
        c1.add_input(NjoyInput("nout", "Output Covariance Tape (NOUT).\nThe resulting multigroup covariance library.", 33, rule=is_int, is_output_file=True, ref="Page 317"))
        c1.add_input(NjoyInput("nin", "Input Covariance Tape (NIN).\nFor chaining multiple runs. Default=0 (None).", 0, rule=is_int, is_input_file=True, ref="Page 317"))
        c1.add_input(NjoyInput("nstan", "Standards Tape (NSTAN).\nUnit for ratio-to-standard data. Default=0 (None).", 0, rule=is_int, is_input_file=True, ref="Page 317"))
        self.add_card(c1, "c1")

        # --- Card 2: Control ---
        c2 = NjoyCard("c2", "Card 2: Processing Options", "Page 317")
        c2.add_input(NjoyInput("matd", "Material ID (MATD).\nThe ENDF MAT number to process.", 125, rule=is_int, options=Data_bases.MAT_DB, ref="Page 317"))
        
        ign_desc = "Neutron Group Structure (IGN).\n1=Arbitrary (User Defined), 2=CSEWG (239), 3=LANL (30).\nIGN=19 reads user grid + ENDF grid."
        c2.add_input(NjoyInput("ign", ign_desc, 2, rule=is_int, options=Data_bases.IGN_DB, ref="Page 317"))
        
        iwt_desc = "Weight Function (IWT).\n6=Default (Thermal-1/E-Fission+Fusion).\n4=Analytic (Card 13b), 1=Tabulated (Card 13)."
        c2.add_input(NjoyInput("iwt", iwt_desc, 6, rule=is_int, options=Data_bases.IWT_DB, ref="Page 317"))
        
        c2.add_input(NjoyInput("iprint", "Print Option (IPRINT).\n0=Minimum (Summary).\n1=Maximum (Detailed Matrices).", 1, rule=is_int, ref="Page 317"))
        c2.add_input(NjoyInput("irelco", "Covariance Form (IRELCO).\n0=Absolute Covariances.\n1=Relative Covariances (Default).", 1, rule=is_int, ref="Page 317"))
        self.add_card(c2, "c2")

        # --- Card 3: NJOY2012+ Required ---
        c3 = NjoyCard("c3", "Card 3: Temperature/Print", "Page 317")
        c3.add_input(NjoyInput("mprint", "Group Avg Print (MPRINT).\n0=Min (Default), 1=Max (Debug averaging).", 0, rule=is_int, ref="Page 317"))
        c3.add_input(NjoyInput("tempin", "Temperature (TEMPIN).\nKelvin. Used for Doppler broadening in weighting flux. Default=300.", 300.0, rule=is_float, ref="Page 317"))
        self.add_card(c3, "c3")

        # --- Card 7: Covariance Control (ENDF-6) ---
        c7 = NjoyCard("c7", "Card 7: Covariance Flags", "Page 318")
        
        iread_desc = (
            "Read Option (IREAD).\n"
            "0 = Program Calculated (Default). Uses standard MTs.\n"
            "1 = User MTs and EKs (Reads Cards 8/9).\n"
            "2 = Calculated + Cross-Material (Reads Card 10)."
        )
        c7.add_input(NjoyInput("iread", iread_desc, 0, rule=is_int, ref="Page 318"))
        
        mfcov_desc = (
            "Covariance File (MFCOV).\n"
            "31 = Nu-bar (Fission Yield).\n"
            "33 = Cross Sections (Standard).\n"
            "34 = Angular Distributions.\n"
            "35 = Energy Distributions.\n"
            "40 = Production Cross Sections."
        )
        c7.add_input(NjoyInput("mfcov", mfcov_desc, 33, rule=is_int, ref="Page 318"))
        
        c7.add_input(NjoyInput("irespr", "Resonance Processing (IRESPR).\n0=Area Sensitivity.\n1=1% Sensitivity Method (Default).", 1, rule=is_int, ref="Page 318"))
        c7.add_input(NjoyInput("legord", "Legendre Order (LEGORD).\nDefault=1. Only used if MFCOV=34 (Angular).", 1, rule=is_int, ref="Page 318"))
        c7.add_input(NjoyInput("ifissp", "Fission Spectrum Sub (IFISSP).\nDefault=-1 (Process subsection containing EFMEAN). Only for MFCOV=35.", -1, rule=is_int, ref="Page 318"))
        
        # UPDATED: Default is now "2.0e6" string to preserve scientific notation
        c7.add_input(NjoyInput("efmean", "Incident Energy (EFMEAN).\neV. Used if IFISSP=-1 to select energy range. Only for MFCOV=35.", "2.0e6", rule=is_float, ref="Page 318"))
        
        c7.add_input(NjoyInput("dap", "Scat. Radius Uncert (DAP).\nFractional uncertainty (e.g. 0.1=10%). Default=0.0 (Use ENDF value).", 0.0, rule=is_float, ref="Page 318"))
        self.add_card(c7, "c7")

        # ======================================================================
        # CONDITIONAL CARDS (IREAD=1)
        # ======================================================================
        
        # --- Card 8: Manual MTs ---
        c8 = NjoyCard("c8", "Card 8: Manual MT Config", "Page 319", active_if=is_iread_1)
        c8.add_input(NjoyInput("nmt", "Number of MTs (NMT).\nCount of reactions to process manually.", 1, rule=is_int, ref="Page 319"))
        c8.add_input(NjoyInput("nek", "Num Derived Ranges (NEK).\nIf 0, all xsecs are independent.\nIf >0, define derived cross-sections (Cards 8b/9).", 0, rule=is_int, ref="Page 319"))
        self.add_card(c8, "c8")

        # --- Card 8a: MT List ---
        c8a = NjoyCard("c8a", "Card 8a: MT List", "Page 319", active_if=is_iread_1)
        c8a.add_input(NjoyInput("mts", "List of MTs.\nSpace separated list of NMT values (e.g. '102 18').", "102", ref="Page 319"))
        self.add_card(c8a, "c8a")

        # --- Card 8b: Derived Energy Bounds ---
        c8b = NjoyCard("c8b", "Card 8b: Derived Energies", "Page 319", active_if=lambda: is_iread_1() and is_nek_nonzero())
        c8b.add_input(NjoyInput("ek", "Energy Bounds (EK).\nList of NEK+1 energy boundaries (eV) for derived cross-sections.", "1.0e-5 2.0e7", ref="Page 319"))
        self.add_card(c8b, "c8b")

        # --- Card 9: Derived Coefficients ---
        c9 = NjoyCard("c9", "Card 9: Coefficients", "Page 319", active_if=lambda: is_iread_1() and is_nek_nonzero())
        c9.add_input(NjoyInput("akxy", "Coefficients (AKXY).\nMatrix of derived coefficients. Enter as space-separated list.", "1.0", ref="Page 319"))
        self.add_card(c9, "c9")

        # ======================================================================
        # CONDITIONAL CARDS (IREAD=2)
        # ======================================================================
        
        # --- Card 10: Cross-Material ---
        c10 = NjoyCard("c10", "Card 10: Cross-Materials", "Page 319", active_if=is_iread_2)
        c10.add_input(NjoyInput("mat1", "Material 1 (MAT1).\nFirst material in correlation pair.", 0, rule=is_int, ref="Page 319"))
        c10.add_input(NjoyInput("mt1", "Reaction 1 (MT1).\nFirst reaction.", 0, rule=is_int, ref="Page 319"))
        c10.add_input(NjoyInput("mat2", "Material 2 (MAT2).\nSecond material in correlation pair.", 0, rule=is_int, ref="Page 319"))
        c10.add_input(NjoyInput("mt2", "Reaction 2 (MT2).\nSecond reaction.", 0, rule=is_int, ref="Page 319"))
        self.add_card(c10, "c10")

        # ======================================================================
        # CONDITIONAL CARDS (NSTAN != 0)
        # ======================================================================
        
        # --- Card 11: Standards ---
        c11 = NjoyCard("c11", "Card 11: Standards", "Page 319", active_if=is_nstan_nonzero)
        c11.add_input(NjoyInput("matb", "Ref Material (MATB).\nStandard reaction referenced in MATD.", 0, rule=is_int, ref="Page 319"))
        c11.add_input(NjoyInput("mtb", "Ref Reaction (MTB).", 0, rule=is_int, ref="Page 319"))
        c11.add_input(NjoyInput("matc", "Std Material (MATC).\nStandard reaction to use instead.", 0, rule=is_int, ref="Page 319"))
        c11.add_input(NjoyInput("mtc", "Std Reaction (MTC).", 0, rule=is_int, ref="Page 319"))
        self.add_card(c11, "c11")

        # ======================================================================
        # GROUP STRUCTURES (Card 12)
        # ======================================================================
        
        # --- Card 12a: Number of Groups ---
        c12a = NjoyCard("c12a", "Card 12a: User Groups Count", "Page 319", active_if=is_ign_user_defined)
        c12a.add_input(NjoyInput("ngn", "Number of Groups (NGN).\nTotal number of user-defined energy groups.", 0, rule=is_int, ref="Page 319"))
        self.add_card(c12a, "c12a")

        # --- Card 12b: Group Bounds ---
        c12b = NjoyCard("c12b", "Card 12b: User Group Bounds", "Page 319", active_if=is_ign_user_defined)
        c12b.add_input(NjoyInput("egn", "Group Bounds (EGN).\nList of NGN+1 energy boundaries (eV) from low to high.", "1.0e-5 2.0e7", ref="Page 319"))
        self.add_card(c12b, "c12b")

        # ======================================================================
        # WEIGHT FUNCTIONS (Card 13)
        # ======================================================================
        
        # --- Card 13: Tabulated Weight ---
        c13 = NjoyCard("c13", "Card 13: Tabulated Weight", "Page 319", active_if=is_iwt_tabulated)
        c13.add_input(NjoyInput("wght", "Weight Function (WGHT).\nTAB1 Record (Energy vs Weight). Must end with /.", "0.0 0.0 /", ref="Page 319"))
        self.add_card(c13, "c13")

        # --- Card 13b: Analytic Weight ---
        c13b = NjoyCard("c13b", "Card 13b: Analytic Params", "Page 320", active_if=is_iwt_analytic)
        c13b.add_input(NjoyInput("eb", "Thermal Break (EB).\neV.", 0.0253, rule=is_float, ref="Page 320"))
        c13b.add_input(NjoyInput("tb", "Thermal Temp (TB).\neV.", 0.0253, rule=is_float, ref="Page 320"))
        c13b.add_input(NjoyInput("ec", "Fission Break (EC).\neV.", 8.2e5, rule=is_float, ref="Page 320"))
        c13b.add_input(NjoyInput("tc", "Fission Temp (TC).\neV.", 1.27e6, rule=is_float, ref="Page 320"))
        self.add_card(c13b, "c13b")

    def add_card(self, card, name=None):
        self.cards.append(card)
        if name: setattr(self, name, card)

    def write(self):
        lines = [self.name]
        
        # Card 1
        c1 = self.c1
        lines.append(f"{c1.nendf.value} {c1.npend.value} {c1.ngout.value} {c1.nout.value} {c1.nin.value} {c1.nstan.value}/")
        
        # Card 2
        c2 = self.c2
        lines.append(f"{c2.matd.value} {c2.ign.value} {c2.iwt.value} {c2.iprint.value} {c2.irelco.value}/")
        
        # Card 3
        c3 = self.c3
        lines.append(f"{c3.mprint.value} {c3.tempin.value}/")
        
        # Card 7 (Standard NJOY2016 Flow)
        c7 = self.c7
        lines.append(f"{c7.iread.value} {c7.mfcov.value} {c7.irespr.value} {c7.legord.value} {c7.ifissp.value} {c7.efmean.value} {c7.dap.value}/")
        
        # Conditionals
        iread = int(c7.iread.value)
        if iread == 1:
            c8 = self.c8
            lines.append(f"{c8.nmt.value} {c8.nek.value}/")
            lines.append(f"{self.c8a.mts.value}/")
            if int(c8.nek.value) > 0:
                lines.append(f"{self.c8b.ek.value}/")
                lines.append(f"{self.c9.akxy.value}/")
        
        if iread == 2:
            c10 = self.c10
            # Simple single entry logic. Real manual implies a loop ending in 0.
            # Here we write the user entry and then 0 termination.
            lines.append(f"{c10.mat1.value} {c10.mt1.value} {c10.mat2.value} {c10.mt2.value}/")
            lines.append("0/") # Terminate list
            
        if int(c1.nstan.value) != 0:
            c11 = self.c11
            lines.append(f"{c11.matb.value} {c11.mtb.value} {c11.matc.value} {c11.mtc.value}/")
            lines.append("0/") # Terminate list
            
        if int(c2.ign.value) in [1, 19]:
            lines.append(f"{self.c12a.ngn.value}/")
            lines.append(f"{self.c12b.egn.value}/")
            
        iwt = int(c2.iwt.value)
        if iwt == 1:
            lines.append(f"{self.c13.wght.value}/")
        elif iwt == 4:
            c = self.c13b
            lines.append(f"{c.eb.value} {c.tb.value} {c.ec.value} {c.tc.value}/")

        return "\n".join(lines)

    @property
    def input_files(self): return [self.c1.nendf.value, self.c1.npend.value]
    @property
    def output_files(self): return [self.c1.nout.value]
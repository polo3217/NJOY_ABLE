MAT_DB = {
    125: "H-1 (Hydrogen-1)",
    128: "He-4 (Helium-4)",
    325: "Li-6 (Lithium-6)",
    328: "Li-7 (Lithium-7)",
    425: "Be-9 (Beryllium-9)",
    600: "C-Nat (Natural Carbon)",
    625: "C-12 (Carbon-12)",
    725: "N-14 (Nitrogen-14)",
    825: "O-16 (Oxygen-16)",
    1325: "Al-27 (Aluminum-27)",
    2600: "Fe-Nat (Natural Iron)",
    9228: "U-235 (Uranium-235)",
    9237: "U-238 (Uranium-238)",
    9437: "Pu-239 (Plutonium-239)"
    
}


GRID_DB = {
    "": "None",
    "0.0253": "Thermal Peak (0.0253 eV)",
    "1.0e-5": "Low Bound (1e-5 eV)",
    "2.0e7": "High Bound (20 MeV)",
    "1.0e-5 0.0253 2.0e7": "Std Anchors", 
    "1.4e7": "Fusion (14 MeV)"
}



MT_DB = {
    1: "Total",
    2: "Elastic Scattering",
    3: "Non-Elastic",
    4: "Total Inelastic",
    16: "(n, 2n)",
    17: "(n, 3n)",
    18: "Fission (Total)",
    19: "(n, f) First Chance",
    102: "(n, gamma) Radiative Capture",
    103: "(n, p)",
    107: "(n, alpha)",
    452: "Nu-Bar (Total)",
    1018: "Chi (Fission Spectrum)"
}


# --- GROUPR DATABASES ---

# ==============================================================================
# GROUPR DATABASES (Detailed from NJOY2016 Manual)
# ==============================================================================

IGN_DB = {
    1: "Arbitrary Structure (Read in)",
    2: "CSEWG 239-Group Structure",
    3: "LANL 30-Group Structure",
    4: "ANL 27-Group Structure",
    5: "RRD 50-Group Structure",
    6: "GAM-I 68-Group Structure",
    7: "GAM-II 100-Group Structure",
    8: "LASER-THERMOS 35-Group Structure",
    9: "EPRI-CPM 69-Group Structure",
    10: "LANL 187-Group Structure",
    11: "LANL 70-Group Structure",
    12: "SAND-II 620-Group Structure",
    13: "LANL 80-Group Structure",
    14: "EURLIB 100-Group Structure",
    15: "SAND-IIA 640-Group Structure",
    16: "Vitamin-E 174-Group Structure",
    17: "Vitamin-J 175-Group Structure",
    18: "XMAS NEA-LANL",
    19: "ECCO 33-Group Structure",
    20: "ECCO 1968-Group Structure",
    21: "TRIPOLI 315-Group Structure",
    22: "XMAS LWPC 172-Group Structure",
    23: "Vit-J LWPC 175-Group Structure",
    24: "SHEM CEA 281-Group Structure",
    25: "SHEM EPM 295-Group Structure",
    26: "SHEM CEA/EPM 361-Group Structure",
    27: "SHEM EPM 315-Group Structure",
    28: "RAHAB AECL 89-Group Structure",
    29: "CCFE 660-Group Structure (30MeV)",
    30: "UKAEA 1025-Group Structure (30MeV)",
    31: "UKAEA 1067-Group Structure (200MeV)",
    32: "UKAEA 1102-Group Structure (1GeV)",
    33: "UKAEA 142-Group Structure (200MeV)",
    34: "LANL 618-Group Structure"
}

IGG_DB = {
    0: "None (No Gamma Processing)",
    1: "Arbitrary Structure (Read in)",
    2: "CSEWG 94-Group Structure",
    3: "LANL 12-Group Structure",
    4: "Steiner 21-Group Gamma-Ray Structure",
    5: "Straker 22-Group Structure",
    6: "LANL 48-Group Structure",
    7: "LANL 24-Group Structure",
    8: "Vitamin-C 36-Group Structure",
    9: "Vitamin-E 38-Group Structure",
    10: "Vitamin-J 42-Group Structure"
}

IWT_DB = {
    0: "Read from Tape (Resonance Flux from NINWT)",
    1: "Read In Smooth Weight Function",
    2: "Constant",
    3: "1/E",
    4: "1/E + Fission Spectrum + Thermal Maxwellian",
    5: "EPRI-CELL LWR",
    6: "(Thermal) -- (1/E) -- (Fission + Fusion)",
    7: "Same as 6 with T-Dep Thermal Part",
    8: "Thermal -- 1/E -- Fast Reactor -- Fission + Fusion",
    9: "CLAW Weight Function",
    10: "CLAW with T-Dependent Thermal Part",
    11: "Vitamin-E Weight Function (ORNL-5505)",
    12: "Vit-E with T-Dep Thermal Part",
    -1: "Compute Flux (Tabulated Input)",
    -4: "Compute Flux (Analytic Input)"
}

MTD_DB = {
    0: "Terminate List (End of Card 9)",
    2: "Elastic Scattering (MT=2)",
    16: "(n,2n) Reaction (MT=16)",
    18: "Total Fission (MT=18)",
    102: "Radiative Capture (n,g) (MT=102)",
    103: "(n,p) Reaction (MT=103)",
    107: "(n,a) Reaction (MT=107)",
    221: "Thermal: Free Gas Model (MT=221)",
    222: "Thermal: Bound Atom Scattering (MT=222)",
    257: "Average Energy (eV) (MT=257)",
    258: "Average Lethargy (MT=258)",
    259: "Average Inverse Velocity (m/s) (MT=259)"
}

# Option 1: AUTOMATIC MACROS (Write "MFD /")
MFD_AUTO_DB = {
    3: "Auto: All Reactions in File 3 (XS)",
    6: "Auto: All Matrix Reactions (MF4/5/6)",
    10: "Auto: All Isotope Productions (MF8)",
    12: "Auto: Photon Prod (Yields, MF12)",
    13: "Auto: Photon Prod (XS, MF13)",
    16: "Auto: Neutron-Gamma Matrix (Yields)",
    17: "Auto: Neutron-Gamma Matrix (XS)",
    18: "Auto: Neutron-Gamma Matrix (MF6)",
    21: "Auto: Proton Production Matrices",
    22: "Auto: Deuteron Production Matrices",
    23: "Auto: Triton Production Matrices",
    24: "Auto: He-3 Production Matrices",
    25: "Auto: Alpha Production Matrices",
    26: "Auto: Residual Nucleus (A>4) Prod"
}

# Option 2: MANUAL SELECTION (Write "MFD MTD MTNAME /")
MFD_MANUAL_DB = {
    3: "File 3: Reaction Cross Sections",
    4: "File 4: Angular Distributions",
    5: "File 5: Energy Distributions",
    6: "File 6: Energy-Angle Distributions",
    8: "File 8: Radioactive Decay / Fission",
    9: "File 9: Multiplicities",
    10: "File 10: Cross Sections (Production)",
    12: "File 12: Photon Production Yields",
    13: "File 13: Photon Production XS",
    23: "File 23: Photon Interaction XS",
    27: "File 27: Atomic Form Factors"
}


# NJOY_Able

> **Enable and Enjoy**

A graphical user interface for the **NJOY Nuclear Data Processing
Code**, designed to simplify input deck generation, automate
parametric studies, and visualize nuclear data processing workflows.

<img width="2816" height="646" alt="njoy_able" src="https://github.com/user-attachments/assets/247b50b6-6b84-4fb1-902a-067ccc762823" />


------------------------------------------------------------------------

## Overview

NJOY_Able provides an intuitive GUI layer on top of NJOY2016, enabling
users to:

-   Graphically construct NJOY input decks
-   Dynamically validate inputs and card dependencies
-   Automate parametric studies
-   Launch NJOY directly from the interface






------------------------------------------------------------------------

## Project Objectives

### 1. Educational Purposes

Lower the barrier to entry for NJOY by visualizing module hierarchies
and associating every card and input with contextual descriptions.

### 2. Automation and Standardization

Ensure input consistency through background validation, manage intra-module
dependencies dynamically, automate sequence generation for sensitivity
studies, and allow direct execution from the GUI.

### 3. Workflow Visualization

Provide a global overview of the cross-section generation pipeline,
allowing users to verify processing-chain coherence.

------------------------------------------------------------------------

## Quick Start

You may either download the main.exe file and execute it or alternatively :

``` bash
git clone https://github.com/polo3217/NJOY_ABLE.git
cd NJOY_Able

cd src
python main.py
```

------------------------------------------------------------------------

## Requirements

-   Python 3.8+
-   Tkinter (usually bundled with Python; Linux users may need
    `sudo apt-get install python3-tk`)
-   NJOY2016 executable (optional for deck generation, required for
    execution)

------------------------------------------------------------------------

## Repository Structure

``` text
/
├── src/                        # Main Application Source Code
│   ├── main.py                 # Application Entry Point
│   ├── gui_app.py              # Main Controller Logic
│   ├── modules/                # NJOY Module Definitions
│   └── gui_components/         # UI Widgets and Helpers
│
├── file_comparison_app/        # Analysis Utility
│   └── comp.py                 # Standalone Diff Tool
│
├── output_exemple/             # Exemple of NJOY_ABLE output
│
├── main.exe/                   # Executable that compile the whole app
│
└── README.md
```

------------------------------------------------------------------------

## Features

### NJOY Input Builder (`src/`)

#### Implemented Modules

-   MODER
-   RECONR
-   BROADR
-   THERMR
-   GROUPR
-   ACER
-   ERRORR
-   HEATR
-   PURR
-   GASPR
-   PLOTR
-   VIEWR
-   UNRESR

#### Key Capabilities

-   Full graphical generation of NJOY input decks
-   Dynamic card activation based on control flags
-   Background type checking and validation
-   Automated parametric studies via Sequential Execution Manager
-   Direct NJOY launch from GUI with runtime error reporting
-   Contextual descriptions for every card and input

<img width="700" height="465" alt="image" src="https://github.com/user-attachments/assets/e160cf0c-614d-428d-9870-be24368197d7" />
<img width="700" height="465" alt="image" src="https://github.com/user-attachments/assets/91a2125e-844d-42a7-9b9a-cc7756b9f60c" />

------------------------------------------------------------------------

## System Architecture

The application follows a hierarchical object-oriented design mirroring
NJOY's logical structure:

    NjoyInputGUI → NjoyModule → NjoyCard → NjoyInput

-   **NjoyInput**: Fundamental parameter with validation logic
-   **NjoyCard**: Logical input block with conditional visibility
-   **NjoyModule**: NJOY processing unit implementing `regenerate()` and
    `write()`

Modules dynamically rebuild their card schemas based on control
parameters, enabling adaptive inputs and automated consistency checks.


------------------------------------------------------------------------

## Contribution Guidelines

Contributions and feedbacks are very welcome, including:

-   GUI improvements
-   Additional NJOY modules (e.g., LEAPR)
-   Documentation enhancements

------------------------------------------------------------------------
## Additional information

Developed at ETH Zuerich and Paul-Scherrer-Institute, Switzerland

------------------------------------------------------------------------



## Disclaimer

NJOY_Able is provided as-is for educational and research purposes. 

While every effort has been made to ensure accuracy and reliability, the authors are not responsible for errors, misuse, or any consequences resulting from the use of this software.  

The development of this tool was AI-assisted for design and documentation.

------------------------------------------------------------------------



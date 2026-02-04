# NJOY_Able

> **Enable and Enjoy**

A graphical interface for the **NJOY Nuclear Data Processing System**, developed to facilitate the generation of input decks and the analysis of nuclear data processing workflows.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.x-blue)


---

## Project Objectives

This project addresses three primary objectives:

### 1. Pedagogical Utility
This GUI significantly lowers the barrier to entry for students and new users of NJOY, by visualizing the hierarchical structure of NJOY modules and linking input fields directly to technical documentation.

### 2. Automation and Standardization
The GUI ensure data integrity and streamline operations by   performing internal background validation to verify input correctness before execution. It dynamically manages intra-module dependencies, automates sequence generation for parametric studies, and allows for the direct launch of simulations.

### 3. Workflow Visualization
To provide an overview of the cross-section generation pipeline. This allows users to verify that the entire processing chain is coherent.

---

## Repository Structure

```text
/
├── src/                        # Main Application Source Code
│   ├── main.py                 # Application Entry Point
│   ├── gui_app.py              # Main Controller Logic
│   ├── modules/                # NJOY Module Definitions (Physics Logic)
│   └── gui_components/         # UI Widgets and Helpers
│
├── file_comparison_app/        # Analysis Utility
│   └── comp.py                 # Standalone Diff Tool for Output Files
│
└── README.md                   # Project Documentation

```

### Key Capabilities

- Full graphical generation of NJOY input decks
- Dynamic card activation based on control flags
- Background validation of all inputs
- Automated parametric studies
- Direct NJOY execution from GUI
- Integrated file comparison utility


------------------------------------------------------------------------

## System Architecture

The application follows a hierarchical object-oriented design:

NjoyInputGUI → NjoyModule → NjoyCard → NjoyInput

Each NJOY module dynamically generates its cards based on control parameters,
allowing adaptive input schemas and automated validation.


------------------------------------------------------------------------

# Contribution Guidelines

Contributions and feedbacks are more than welcome, should they concern the GUI,
the development of additional modules (LEAPR etc...) or any other suggestions.

------------------------------------------------------------------------



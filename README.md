# NJOY Input Builder & Analysis Suite

A graphical interface for the **NJOY Nuclear Data Processing System**, developed to facilitate the generation of input decks and the analysis of nuclear data processing workflows.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Project Objectives

This software addresses the complexity of the legacy "card-image" input format used by NJOY. The primary objectives are:

### 1. Automation and Standardization
To reduce human error and syntax issues inherent in manual text file creation. The system enforces formatting rules, manages module dependencies, and automates sequence generation for parametric studies.

### 2. Pedagogical Utility
To serve as an interactive reference for nuclear engineering students and professionals. By visualizing the hierarchical structure of NJOY modules and linking input fields directly to technical documentation, the interface reinforces the underlying physics of the processing steps.

### 3. Workflow Visualization
To provide a macroscopic view of the nuclear data processing pipeline. This allows users to verify the logical flow of data—from resonance reconstruction to multigroup averaging—within a unified environment.

---

## Repository Structure

```text
/
├── src/                        # Main Application Source Code
│   ├── main.py                 # Application Entry Point
│   ├── gui_app.py              # Main Controller Logic
│   ├── modules/                # NJOY Module Definitions
│   └── gui_components/         # UI Widgets and Helpers
│
├── file_comparison_app/        # Analysis Utility
│   └── main.py                 # Standalone Diff Tool for Output Files
│
└── README.md                   # Project Documentation

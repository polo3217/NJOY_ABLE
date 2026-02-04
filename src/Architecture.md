# System Architecture

This document details the software design patterns and internal logic of
the **NJOY_Able** application. The system uses a hierarchical
Object-Oriented framework designed to mirror the structure of a
nuclear data processing input deck while abstracting legacy formatting
complexities.

## 1. Core Abstraction Model

The application state is managed through a four-tier hierarchy.
This design ensures that the Graphical User Interface (GUI) remains
synchronized with the underlying data structure required for the input
stream.

### Hierarchy

`NJOYInputGUI` (Controller) → `NjoyModule` → `NjoyCard` → `NjoyInput`

------------------------------------------------------------------------

### 1.1 Basic Unit: `NjoyInput`

*Defined in: `src/class_def.py`*

The `NjoyInput` class encapsulates a single fundamental data parameter
(e.g., a floating-point value, an integer flag, or a character string).

**Attributes** - `name` (str): Internal variable identifier used for
logic references. - `value` (any): The current data stored in memory. -
`description` (str): Technical documentation displayed via interface
tooltips. - `rule` (callable): A validation function returning a Boolean
based on data integrity.

**Behavior**\
Acts as the Model in the MVC pattern for individual fields. Modification
of the GUI entry directly updates this object's `value` attribute.

------------------------------------------------------------------------

### 1.2 Logical Block: `NjoyCard`

*Defined in: `src/class_def.py`*

An `NjoyCard` represents a logical grouping of inputs, corresponding to
a single record or line in the target input file.

**Attributes** - `inputs` (list): Collection of `NjoyInput` objects. -
`active_if` (callable): Lambda hook controlling card visibility.

**Behavior** - Aggregates child inputs into a delimited string during
write phase. - Evaluates `active_if()` before rendering; inactive cards
are excluded from GUI and export.

------------------------------------------------------------------------

### 1.3 Module: `NjoyModule`

*Defined in: `src/modules/*.py`*

Each processing module is defined as a class managing the data flow and
logic for a specific calculation step.

**Key Lifecycle Methods** - `__init__`: Establishes static metadata. -
`regenerate()`: Core logic engine reconstructing card lists dynamically
based on control variables. - `write()`: Serializes active cards into
formatted text blocks.

------------------------------------------------------------------------

## 2. The Regenerative State Model

To handle complex inter-parameter dependencies, the application relies
on a regenerative state cycle.

### 2.1 Regeneration Cycle

1.  User modifies a value.
2.  UI triggers callback.
3.  `regenerate()` executes:
    -   Reads control parameters.
    -   Clears existing cards.
    -   Rebuilds required cards.
    -   Preserves previous values.
4.  GUI updates rendered widgets.

------------------------------------------------------------------------

### 2.2 Serialization Phase

1.  Iterate active modules.
2.  Invoke `write()`.
3.  Filter cards by `active_if`.
4.  Collect `NjoyInput` values.
5.  Concatenate into ASCII-compliant output.

------------------------------------------------------------------------

## 3. Module Implementation Interface

### Initialization

``` python
class GenericModule:
    def __init__(self):
        self.name = "module_name"
        self.description = "Technical description..."
        self.cards = []
        self.regenerate()
```

### Logic Implementation (`regenerate()`)

-   Define static cards.
-   Read control variables.
-   Generate dynamic cards.
-   Register cards in `self.cards`.

### Serialization (`write()`)

-   Write module header.
-   Loop through cards.
-   Format inputs.
-   Append termination string.

------------------------------------------------------------------------

## 4. Auxiliary Systems

### Sequential Execution Manager

*Location: `src/gui_components/sequential_runner.py`*

-   Discovers inputs via inspection.
-   Generates Cartesian parameter matrices.
-   Executes batch cycles: State Modification → Input Generation →
    Process Execution → State Restoration.

### Project Manager

*Location: `src/gui_components/project_manager.py`*

Handles JSON-based state preservation by extracting raw `NjoyInput`
values and mapping them by Module/Card identifiers, enabling full
workspace restoration including dynamic structures.

------------------------------------------------------------------------

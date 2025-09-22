# Unit Commitment Project

## 📌 Overview
This project implements the **Unit Commitment (UC) problem** in power systems, formulated as a **Mixed-Integer Linear Programming (MILP)** model and solved using **Gurobi**.  

The goal is to determine which power generation units should be **ON** or **OFF** in each time period to:  
- Meet electricity demand,  
- Minimize total operating costs,  
- Respect key technical and economic unit constraints.  

The project includes:  
- **A small illustrative example** with full Excel input/output files.  
- **A larger case study**, where input data are currently provided in **illustrative form (screenshot)**.

---

## ⚡ Unit Commitment Features
Each conventional generation unit is characterized by:  
- **Commitment status (ON/OFF)**  
- **No-load (fixed) operating cost**  
- **Start-up and shut-down costs**  
- **Minimum stable generation**  
- **Ramp-up and ramp-down limits**  
- **Minimum up/down times**  
- **Optional constraints**: must-run/must-hold periods, fuel or crew limitations (ignored in this implementation)

These features introduce complexity through **binary decision variables** and **temporal coupling** between periods, which are fully handled in this MILP formulation.

---

## 🏗️ Project Structure
```bash
unit-commitment-project/
│
├── README.md                 # Project description and instructions
├── requirements.txt          # Python dependencies
├── LICENSE                   # License information
│
├── scripts/
│   ├── simple_case/
│   │   ├── unitcommitment_simplecase.py
│   │   └── README.md
│   ├── main_case/
│   │   ├── main_unit_commitment.py
│   │   └── README.md
│ 
├── inputs/
│   ├── unitC_LARGE_STATEMENT.png    # Input for the large case study (illustrative screenshot)
│   ├── simple_demo.xlsx         # Input for the small demo code example
│
├── outputs/
│   ├── UnitCOMMITMENT_MAIN_RESULTS.xlsx   # Output for the large case study
│   ├── simple_case_output.xlsx        # Output for the small example
```
---

## 🚀 Running the Project

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```
2. Run the small illustrative example:
```bash
python scripts/simple_example.py
```
3. python scripts/main_unit_commitment.py
```bash
python scripts/main_unit_commitment.py
```
## 🖥️ Solver Requirements

- The **main_unit_commitment.py** script is written using **Gurobi** and is intended for **large-scale problems**.  
  - A valid **Gurobi license** is required to run this script.  
  - The large-scale problem cannot be solved using free/open-source solvers due to its size and complexity.

- The **simple_example.py** script is implemented in **Pyomo** and demonstrates a **small illustrative problem** (3 time periods).  
  - It can be solved using **open-source solvers** like **GLPK** or **CBC**, making it accessible without a commercial license.  
  - This allows users to explore the model structure and test the workflow on a small scale.

## 📚 Dependencies

The project requires the following Python packages and tools:

- **Python ≥ 3.8** – Recommended for compatibility with all dependencies.  
- **pandas** – For reading, writing, and manipulating Excel and tabular data.  
- **numpy** – For numerical operations and array handling.  
- **pyomo** – To formulate and solve optimization models.  
- **gurobipy** – Python interface to Gurobi solver for mixed-integer programming.  
- **xlsxwriter** – For exporting results to formatted Excel files.  
- **openpyxl** – For reading and writing Excel `.xlsx` files.  
- **GLPK** – Open-source solver for linear and mixed-integer programming (alternative to Gurobi).  

Optional but recommended:   
- **time** (standard library) – For measuring execution time.  

> ⚠️ Ensure that you have a valid Gurobi license installed before running the scripts.

---

## 📄 License

This project is available under the **MIT License**. See the `LICENSE` file for details.

---

## ⚠️ Notes

- The **small example** is fully runnable with provided Excel input/output files.  
- The **large case study** demonstrates the structure and features of a real-world scenario, but full input data are **not included**.  
- Optional constraints like fuel or crew limitations are **ignored** in this implementation.  
- This project focuses on the **mathematical and operational aspects** of Unit Commitment without modeling network constraints.

# Simple Case - Unit Commitment Project

## Input Data

The simple illustrative case uses demo data provided in the Excel file `UnitCdemo.xlsx`.  

- The input values are **artificially generated** and **do not represent real-world market data**.  
- The file contains essential parameters such as:
  - Generator minimum and maximum capacities
  - Production costs
  - Startup costs and up/down times
  - Initial generator status
  - Demand parameters and benefit coefficients  

Since this is a demo, there is **no standard "official" input file**. Users can modify the demo data or create new input Excel files following the same format and logic to test different scenarios.

## Solver

The simple case is solved using **Pyomo** with the **GLPK** solver:

- Pyomo allows modeling the **unit commitment problem as a Mixed-Integer Linear Program (MILP)**.  
- GLPK is an open-source MILP solver; no commercial license is required.  
- Ensure Pyomo and GLPK are installed and accessible in your Python environment.

## Notes

- Generator on/off statuses are modeled as **binary variables**.  
- To compute **shadow prices (LMPs)**, the binary commitment variables are treated as **parameters fixed to their optimal solution**, enabling calculation of locational marginal prices in a linearized problem.  
- Outputs include:
  - Unit commitment schedule (ON/OFF) for each generator
  - Production and demand summaries
  - Shadow prices / locational marginal prices
  - Ex-post social welfare, producer profits, and consumer utility  
- Execution time is minimal due to the small size of the illustrative problem.
## Shadow Prices (LMPs)

In the simple case, **shadow prices (locational marginal prices, LMPs)** are used to calculate **ex-post producer profits and consumer utility**.  

- Since the unit commitment problem involves **binary on/off variables** for generators, the problem is inherently **mixed-integer**.  
- To compute shadow prices in a **linearized framework**, the binary commitment variables are **treated as parameters fixed to their optimal solution**.  
- This allows solving a **linearized problem** where the shadow prices (LMPs) can be computed consistently with the actual unit commitment.  
- The resulting shadow prices are then used in the code to calculate:
  - **Ex-post producer profit per period**  
  - **Ex-post consumer utility per period**  
  - **Total social welfare**  

These calculations are included in the output Excel file (`simple_output.xlsx`) under the “Ex-post Summary” sheet.

### Why This Approach

- Directly computing LMPs in a mixed-integer problem is not straightforward because dual variables are not defined for integer constraints.  
- Fixing the commitment decisions to their optimal integer values converts the problem to **linear**, allowing dual variables (shadow prices) to be extracted.  
- This approach ensures that **ex-post financial metrics** are consistent with the chosen unit commitment schedule.


## How to Run

1. Ensure all dependencies are installed (see `requirements.txt`):
   - Python ≥ 3.8  
   - pandas  
   - numpy  
   - pyomo  
   - xlsxwriter  
   - GLPK solver  

2. Update the input file path in `simple_example.py` if necessary.  

3. Run the script:
   ```bash
   python simple_example.py
4. Results will be saved in the outputs folder as an Excel file
   ```bash
   simple_output.xlsx

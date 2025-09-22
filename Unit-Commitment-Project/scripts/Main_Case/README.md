# Main Case - Unit Commitment Project

## Input Data

The input data for the main case is provided in the same format as the small illustrative demo case. It follows the structure commonly used in the U.S. electricity market (ISO-style data), but **all values are artificially generated** and **do not represent real-world data**.  

A screenshot of the demo input has been included to illustrate the structure and format. By following the same logic and format, you can create input data for the main case. Make sure that all necessary parameters (generator limits, costs, up/down times, demand, etc.) are included in the Excel file.

## Solver

This project uses **Gurobi** to solve the main unit commitment problem.  

- Gurobi is a powerful commercial solver capable of handling mixed-integer linear programming (MILP) problems efficiently.  
- **A valid Gurobi license is required** to run the main case.  
- Ensure Gurobi is installed and properly configured in your Python environment.
  
## Notes

- The input data must follow the same structure as the demo case. A screenshot of the demo input is included to help replicate the format. All values are **artificially generated** and **do not reflect real-world market data**.  
- The model is formulated as a **Mixed-Integer Linear Program (MILP)**. Generator on/off statuses are modeled as **binary variables**.  
- To compute **shadow prices (LMPs)**, the binary commitment variables are treated as **parameters fixed to their optimal solution**. This allows the calculation of locational marginal prices in a linearized problem.  
- The main case is solved using **Gurobi**, a commercial MILP solver. **A valid Gurobi license is required**. Ensure Gurobi is installed and configured in your Python environment.  
- Outputs include unit commitment schedules, production and demand summaries, LMPs/shadow prices, and ex-post social welfare, producer profits, and consumer utility.  
- Execution time may vary depending on the problem size and solver configuration.  

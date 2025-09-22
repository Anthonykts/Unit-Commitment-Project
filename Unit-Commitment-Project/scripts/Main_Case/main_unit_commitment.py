import pandas as pd
from gurobipy import *
import gurobipy as gp
import time

df = pd.read_excel("inputs/...xlsx", header=0, sheet_name='Sheet1')

model = gp.Model("UnitCommitment")
start_time = time.time()
time_periods = list(range(1, 25))
generator_numbers = df.iloc[2:9, 0].tolist()
generator_mapping = {t: generator_numbers for t in time_periods}
demand_number = df.iloc[11, 0]
demand_number_list = [demand_number]
offers_per_generator = 5
offers_per_demand = 1
num_offers = {generator: offers_per_generator for generator in generator_numbers}

# PARAMETER'S VALUES
Pdmax = df.loc[11, 'Unnamed: 1':'Unnamed: 24'].tolist()
Bd = df.loc[13, 'Unnamed: 1':'Unnamed: 24'].tolist()
Pgmin = df.loc[2:8, 'Unnamed: 2'].tolist()
Pgmax = df.loc[2:8, 'Unnamed: 1'].tolist()
TgUP = df.loc[2:8, 'Unnamed: 11'].tolist()
TgDN = df.loc[2:8, 'Unnamed: 12'].tolist()
CgUP = df.loc[2:8, 'Unnamed: 9'].tolist()
CgDN = df.loc[2:8, 'Unnamed: 10'].tolist()
Ug0 = df.loc[2:8, 'Unnamed: 13'].tolist()
RgUP = df.loc[2:8, 'Unnamed: 15'].tolist()
RgDN = df.loc[2:8, 'Unnamed: 16'].tolist()
CgNL = df.loc[2:8, 'Unnamed: 8'].tolist()
Pg0 = df.loc[2:8, 'Unnamed: 14'].tolist()
Cgb1 = df.loc[2:8, 'Unnamed: 3'].tolist()
Cgb2 = df.loc[2:8, 'Unnamed: 4'].tolist()
Cgb3 = df.loc[2:8, 'Unnamed: 5'].tolist()
Cgb4 = df.loc[2:8, 'Unnamed: 6'].tolist()
Cgb5 = df.loc[2:8, 'Unnamed: 7'].tolist()

# Setting Parameters into dictionaries

Cgb = {}
for i, generator in enumerate(generator_numbers, start=1):
    Cgb[generator] = {1: Cgb1[i-1], 2: Cgb2[i-1], 3: Cgb3[i-1], 4: Cgb4[i-1], 5: Cgb5[i-1]}
Cg_b = {}
for g in generator_numbers:
    for b in range(1, offers_per_generator + 1):
        for t in time_periods:
            Cg_b[g, b, t] = Cgb[g][b]
Pg_max = {}
for g in generator_numbers:
    for b in range(1, offers_per_generator + 1):
        for t in time_periods:
            Pg_max[g, b, t] = Pgmax[g-1]
Pg_min = {}
for g in generator_numbers:
    Pg_min[g] = Pgmin[g-1]
Pd_max = {}
for d in demand_number_list:
    for b in range(1, offers_per_demand + 1):
        for t in time_periods:
            Pd_max[d, b, t] = Pdmax[t-1]
B_d = {}
for d in demand_number_list:
    for b in range(1, offers_per_demand + 1):
        for t in time_periods:
            B_d[d, b, t] = Bd[t-1]
Cg_NL ={}
for g in generator_numbers:
    for t in time_periods:
        Cg_NL[g,t]= CgNL[g-1]
# DEFINE THE DECISION VARIABLES

# BINARIES
u_g = {}
for t in range(1, len(time_periods) + 1):
    for idx, g in enumerate(generator_numbers, start=1):
        u_g[g, t] = model.addVar(vtype=GRB.BINARY, name=f"u_g_{g}_{t}")

# Start Up COST Decision Variable
cg_UP = {}
for t in range(1, len(time_periods) + 1):
    for idx, g in enumerate(generator_numbers, start=1):
        cg_UP[g, t] = model.addVar(vtype=GRB.CONTINUOUS, name=f"cgUP[{g},{t}]")
# Shut Down COST Decision Variable
cg_DN = {}
for t in range(1, len(time_periods) + 1):
    for idx, g in enumerate(generator_numbers, start=1):
        cg_DN[g, t] = model.addVar(vtype=GRB.CONTINUOUS,  name=f"cgDN[{g},{t}]")
# Define decision variables for generators
p_g = {}
for t in range(1, len(time_periods) + 1):
    for idx, g in enumerate(generator_numbers, start=1):  # Loop over generators
        for b in range(1, offers_per_generator + 1):  # Loop over offers
            p_g[g, b, t] = model.addVar(vtype=GRB.CONTINUOUS,  name=f"p_g_{g}_{t}_{b}")
# Define decision variables for demands
p_d = {}
for t in range(1, len(time_periods) + 1):
    for idx, d in enumerate(range(1, demand_number + 1), start=1):  # Loop over demand nodes
        for b in range(1, offers_per_demand + 1):  # Loop over offers
            p_d[d, b, t] = model.addVar(vtype=GRB.CONTINUOUS,  name=f"p_d_{d}_{t}_{b}")

constraints = {}
# Constraint 1: Power Balance Constraint
for t in range(1, len(time_periods) + 1):
    constraint_name1 = f"Power_Balance_{t}"
    constraint_expr1 = quicksum(p_g[g, b, t] for g in generator_numbers for b in range(1, offers_per_generator + 1)) - quicksum(p_d[d, b, t] for d in range(1, demand_number + 1) for b in range(1, offers_per_demand + 1))
    constraints[constraint_name1] = model.addConstr(constraint_expr1 == 0, name=constraint_name1)
# Constraint 2: Power demand limits
constraint_counter2 = 0
for t in range(1, len(time_periods) + 1):
    for d in demand_number_list:
        for b in range(1, offers_per_demand + 1):
            # Lower limit constraint
            constraint_name2a = f"Power_Demand_Limit_lower{d}_{b}_{t}"
            constraint_expression2 = f"{p_d[d,b,t]} >= 0"
            constraints[constraint_name2a] = model.addConstr(p_d[d, b, t] >= 0, name=constraint_name2a)
            # Upper limit constraint
            constraint_name2b = f"Power_Demand_Limit_Upper_{d}_{b}_{t}"
            constraint_expression3 = f"{p_d[d,b,t]} <= {Pd_max[d, b, t]}"
            constraints[constraint_name2b] = model.addConstr(p_d[d, b, t] <= Pd_max[d, b, t], name=constraint_name2b)
# Constraint 3: Power Generation Upper and Lower Limits
constraint_counter3 = 0
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        for b in range(1, offers_per_generator + 1):
            # Lower limit constraint
            constraint3_name_lower = f"Power_Gen_Limit_Lower_{g}_{b}_{t}"
            constraint_expression_lower = p_g[g, b, t] >= 0
            constraints[constraint3_name_lower] = model.addConstr(constraint_expression_lower,name=constraint3_name_lower)
            # Upper limit constraint
            constraint3_name_upper = f"Power_Gen_Limit_Upper_{g}_{b}_{t}"
            constraint_expression_upper = p_g[g, b, t] <= Pg_max[g, b, t] * u_g[g, t]
            constraints[constraint3_name_upper] = model.addConstr(constraint_expression_upper,name=constraint3_name_upper)
# Constraint 4: Minimum Stable Generation
constraint_counter4 = 0
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        constraint_name4 = f"Power_Gen_Lower_Bound_{g}_{b}_{t}"
        constraint_expression4 = Pg_min[g] * u_g[g, t] <= quicksum(p_g[g, b, t] for b in range(1, offers_per_generator + 1))
        constraints[constraint_name4] = model.addConstr(constraint_expression4, name=constraint_name4)
# Constraint 5: Startup Cost Non-negativity
constraint_counter5 = 0
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        constraint_name5 = f"Startup_Cost_Nonnegativity_UP_{g}_{t}"
        constraint_expression5 = cg_UP[g, t] >= 0
        constraints[constraint_name5] = model.addConstr(constraint_expression5, name=constraint_name5)
# Constraint 6: Startup Cost Lower Bound
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        if t - 1 > 0:
            constraint_name6 = f"Startup_Cost_Lower_Bound_{g}_{t}"
            constraint_expr6 = (u_g[g, t] - u_g[g, t - 1]) * CgUP[g - 1]
            constraints[constraint_name6] = model.addConstr(cg_UP[g, t] >= constraint_expr6, name=constraint_name6)
        else:
            constraint_name6 = f"Startup_Cost_Lower_Bound_{g}_{t}"
            constraint_expr6 = (u_g[g, t] - Ug0[g - 1]) * CgUP[g - 1]
            constraints[constraint_name6] = model.addConstr(cg_UP[g, t] >= constraint_expr6, name=constraint_name6)
# Constraint 7: Shut Down Cost Non-negativity
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        constraint_name8 = f"SHUT_DOWN_COST_Nonnegativity_UP_{g}_{t}"
        constraint_expression7 = cg_DN[g, t] >= 0
        constraints[constraint_name8] = model.addConstr(constraint_expression7, name=constraint_name8)
# Constraint 8: Shut Down Cost Lower Bound
constraint_counter8 = 0
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        if t - 1 > 0:
            constraint_name9 = f"ShutDown_Cost_Lower_Bound_{g}_{t}"
            constraint_expr9 = (u_g[g, t] - u_g[g, t - 1]) * (-CgDN[g - 1])
            constraints[constraint_name9] = model.addConstr(cg_DN[g, t] >= constraint_expr9, name=constraint_name9)
        else:
            constraint_name9 = f"ShutDown_Cost_Lower_Bound_{g}_{t}"
            constraint_expr9 = (u_g[g, t] - Ug0[g - 1]) * (- CgDN[g - 1])
            constraints[constraint_name9] = model.addConstr(cg_DN[g, t] >= constraint_expr9,name=constraint_name9)
# Constraint 9: Ramp Up Rates
constraint_counter13 = 0
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        if t - 1 > 0:
            constraint_name9 = f"Ramp_Up_Rates_{g}_{t}"
            constraint_expr9 = quicksum(p_g[g, b, t] for b in range(1, offers_per_generator + 1)) - quicksum(p_g[g, b, t-1] for b in range(1, offers_per_generator + 1)) - RgUP[g-1]
            constraints[constraint_name9] = model.addConstr(constraint_expr9 <= 0, name=constraint_name9)
        else:
            constraint_name9 = f"Ramp_Up_Rates_{g}_{t}"
            constraint_expr9 = quicksum(p_g[g, b, t] for b in range(1, offers_per_generator + 1)) - Pg0[g-1] - RgUP[g-1]
            constraints[constraint_name9] = model.addConstr(constraint_expr9 <= 0, name=constraint_name9)
# Constraint 10: Ramp Down Rates
constraint_counter14 = 0
for t in range(1, len(time_periods) + 1):
    for g in generator_numbers:
        if t - 1 > 0:
            constraint_name10 = f"Ramp_Down_Rates_{g}_{t}"
            constraint_expr10 = quicksum(p_g[g, b, t-1] for b in range(1, offers_per_generator + 1)) - quicksum(p_g[g, b, t] for b in range(1, offers_per_generator + 1)) - RgDN[g-1]
            constraints[constraint_name10] = model.addConstr(constraint_expr10 <= 0, name=constraint_name10)
        else:
            constraint_name10 = f"Ramp_Down_Rates_{g}_{t}"
            constraint_expr10 = Pg0[g-1] - quicksum(p_g[g, b, t] for b in range(1, offers_per_generator + 1)) - RgDN[g-1]
            constraints[constraint_name10] = model.addConstr(constraint_expr10 <= 0, name=constraint_name10)
# Constraint 11: Constraint for Minimum UpTime
for g in generator_numbers:
    for t in range(1, len(time_periods) - TgUP[g-1] + 2):
        if t - 1 > 0:
            constraint_name11 = f"Minimum_UpTime_Constraint_{g}_{t}_a"
            constraint_expr11 = quicksum(u_g[g, r] for r in range(t, t + TgUP[g-1])) - TgUP[g-1] * (u_g[g, t] - u_g[g, t - 1])
            constraints[constraint_name11] = model.addConstr(constraint_expr11 >= 0, name=constraint_name11)
        else:
            constraint_name11 = f"Minimum_UpTime_Constraint_{g}_{t}_b"
            constraint_expr11 = quicksum(u_g[g, r] for r in range(t, t + TgUP[g-1])) - TgUP[g-1] * (u_g[g, t] - Ug0[g-1])
            constraints[constraint_name11] = model.addConstr(constraint_expr11 >= 0, name=constraint_name11)

# Constraint 12: Constraint for Minimum DownTime
for g in generator_numbers:
    for t in range(1, len(time_periods) - TgDN[g - 1] + 2):
        if t - 1 > 0:
            constraint_name12a = f"Minimum_DownTime_Constraint_{g}_{t}_a"
            constraint_expr12a = quicksum(1 - u_g[g, r] for r in range(t, t + TgDN[g - 1])) + TgDN[g - 1] * (u_g[g, t] - u_g[g, t - 1])
            constraints[constraint_name12a] = model.addConstr(constraint_expr12a >= 0, name=constraint_name12a)
        else:
            constraint_name12b = f"Minimum_DownTime_Constraint_{g}_{t}_b"
            constraint_expr12b = quicksum(1 - u_g[g, r] for r in range(t, t + TgDN[g - 1])) + TgDN[g - 1] * (
                        u_g[g, t] - Ug0[g - 1])
            constraints[constraint_name12b] = model.addConstr(constraint_expr12b >= 0, name=constraint_name12b)

# Constraint 13: Must run Constraint
constraint_counter11 = 0
for g in generator_numbers:
    for t in range(len(time_periods) - TgUP[g - 1] + 2, len(time_periods) + 1):
        if t - 1 > 0:
            constraint_name13a = f"Must_Run_Constraint_{g}_{t}_a"
            constraint_expr13a = quicksum(u_g[g, r] - (u_g[g, t] - u_g[g, t - 1]) for r in range(t, len(time_periods) + 1))
            constraints[constraint_name13a] = model.addConstr(constraint_expr13a >= 0, name=constraint_name13a)
        else:
            constraint_name13b = f"Must_Run_Constraint_{g}_{t}_b"
            constraint_expr13b = quicksum(u_g[g, r] - (u_g[g, t] - Ug0[g - 1]) for r in range(t, len(time_periods) + 1))
            constraints[constraint_name13b] = model.addConstr(constraint_expr13b >= 0, name=constraint_name13b)

# Constraint 13: Must stop Constraint
constraint_counter12 = 0
for g in generator_numbers:
    for t in range(len(time_periods) - TgDN[g - 1] + 2, len(time_periods) + 1):
        if t - 1 > 0:
            constraint_name14a = f"Must_Stop_Constraint_{g}_{t}_a"
            constraint_expr14a = quicksum(1 - u_g[g, r] - (u_g[g, t - 1] - u_g[g, t]) for r in range(t, len(time_periods) + 1))
            constraints[constraint_name14a] = model.addConstr(constraint_expr14a >= 0, name=constraint_name14a)
        else:
            constraint_name14b = f"Must_Stop_Constraint_{g}_{t}_b"
            constraint_expr14b = quicksum(1 - u_g[g, r] - (Ug0[g - 1] - u_g[g, t]) for r in range(t, len(time_periods) + 1))
            constraints[constraint_name14b] = model.addConstr(constraint_expr14b >= 0, name=constraint_name14b)

# OBJECTIVE FUNCTION
SW_expr = (
    quicksum(B_d[d, b, t] * p_d[d, b, t] for d in demand_number_list for t in range(1, len(time_periods) + 1) for b in range(1, offers_per_demand + 1)) -
    quicksum(Cg_b[g, b, t] * p_g[g, b, t] for g in generator_numbers for t in range(1, len(time_periods) + 1) for b in range(1, offers_per_generator + 1)) -
    quicksum(cg_UP[g, t] for g in generator_numbers for t in range(1, len(time_periods) + 1)) -
    quicksum(cg_DN[g, t] for g in generator_numbers for t in range(1, len(time_periods) + 1)) -
    quicksum(Cg_NL[g, t]* u_g[g, t] for g in generator_numbers for t in range(1, len(time_periods) + 1)))

# optimizing
model.setObjective(SW_expr, GRB.MAXIMIZE)
model.optimize()

# Calculate and print the total demand with flexibility and total generation cost over all periods
total_consumption_benefit = sum(B_d[d, b, t] * p_d[d, b, t].x for d in demand_number_list for t in range(1, len(time_periods) + 1) for b in range(1, offers_per_demand + 1))
total_generation_cost = sum(Cg_b[g, b, t] * p_g[g, b, t].x for g in generator_numbers for t in range(1, len(time_periods) + 1) for b in range(1, offers_per_generator + 1))
cg_UP_component = sum(cg_UP[g, t].X for g in generator_numbers for t in range(1, len(time_periods) + 1))
cg_DN_component = sum(cg_DN[g, t].X for g in generator_numbers for t in range(1, len(time_periods) + 1))
Cg_NL_component = sum(Cg_NL[g, t] * u_g[g, t].X for g in generator_numbers for t in range(1, len(time_periods) + 1))
# Calculate the total
total_additional_costs = cg_UP_component + cg_DN_component + Cg_NL_component
total_generation_cost_with_additional = total_generation_cost + total_additional_costs

end_time = time.time()
execution_time = end_time - start_time

# OUTPUT SAVE
results_data = pd.DataFrame()
status_data = pd.DataFrame()
for t in time_periods:
    pg_values = []
    pd_values = []
    cgup_values = []
    cgdn_values = []
    ug_values = []
    ug_status = []

    for g in generator_numbers:
        for b in range(1, offers_per_generator + 1):
            pg_values.append(p_g[g, b, t].X)
    for d in demand_number_list:
        for b in range(1, offers_per_demand + 1):
            pd_values.append(p_d[d, b, t].X)
    for g in generator_numbers:
        cgup_values.append(cg_UP[g, t].X)
        cgdn_values.append(cg_DN[g, t].X)
        ug_value = u_g[g, t].X
        # Append ug_value and its status indication
        ug_values.append(ug_value)
        ug_status.append("ON" if ug_value == 1 else "OFF")

    # Create DataFrames for this time period
    time_data1 = pd.DataFrame({
        "Time Period": [f"Time Period {t}" for _ in range(len(generator_numbers) * offers_per_generator)],
        "Offer Number": [f"Offer {b}" for _ in generator_numbers for b in range(1, offers_per_generator + 1)],
        "Generator": [f"G {g}" for g in generator_numbers for _ in range(1, offers_per_generator + 1)],
        "Power Generation (Pg)": [f"{p_g[g, b, t].X} MW" for g in generator_numbers for b in range(1, offers_per_generator + 1)]})
    time_data2 = pd.DataFrame({
        "Time Period": [f"Time Period {t}"],
        "Demand Node": [f"D{d}" for d in demand_number_list for _ in range(1, offers_per_demand + 1)],
        "Bid number": [f"Bid {b}" for _ in demand_number_list for b in range(1, offers_per_demand + 1)],
        "Power Demand (Pd)": [f" {p_d[d, b, t].X} MW" for d in demand_number_list for b in range(1, offers_per_demand + 1)]})
    time_data3 = pd.DataFrame({
        "Time Period": [f"{t}"] * len(generator_numbers),  # Repeat time period for each generator
        "Generator": [f"G{g}" for g in generator_numbers],
        "Binary Variable (Ug)": ug_values,
        "Status(ON/OFF)": ug_status,
        "Startup Cost (€)": [f"{value}€" for value in cgup_values],  # Format startup costs
        "Shutdown Cost (€)": [f"{value}€" for value in cgdn_values]  # Format shutdown costs
    })

    time_data = pd.concat([time_data2, time_data1], axis=1)
    results_data = pd.concat([results_data, time_data], ignore_index=True)
    status_data = pd.concat([status_data, time_data3], ignore_index=True)
total_startup_cost = sum(cg_UP[g, t].X for g in generator_numbers for t in time_periods)
total_shutdown_cost = sum(cg_DN[g, t].X for g in generator_numbers for t in time_periods)
df_sw_exec = pd.DataFrame({
    'Social Welfare (€)': [f"{model.objVal}€"],
    'Total Consumption Benefit (€)': [f"{total_consumption_benefit}€"],
    'Total Generation Cost (€)': [f"{total_generation_cost}€"],
    'Total Additional Costs (€)': [f"{total_additional_costs}€"],
    'Total Generation Cost with Additional (€)': [f"{total_generation_cost_with_additional}€"],
    'Execution Time (sec)': [f"{execution_time:.2f} sec"]

}, index=["Summary"])

total_cost_df = pd.DataFrame({
    'Total Startup Cost (€)': [f"{total_startup_cost}€"],
    'Total Shutdown Cost (€)': [f"{total_shutdown_cost}€"],
    'Total non load Cost (€)': [f"{Cg_NL_component}€"],
    'Total Additional Costs (€)': [f"{total_additional_costs}€"],
}, index=["Summary"])

with pd.ExcelWriter("UnitCOMMITMENT_MAIN_RESULTS.xlsx") as writer:
    results_data.to_excel(writer, index=False, sheet_name='ACCEPTED QUANTITIES')
    status_data.to_excel(writer, index=False, sheet_name='UNIT STATUS')
    df_sw_exec.to_excel(writer, index=False, sheet_name='WELFARE')
    total_cost_df.to_excel(writer, index=False, startcol=7, startrow=0, sheet_name='UNIT STATUS')


import pandas as pd
import time
from pyomo.environ import ConcreteModel, Var, Binary, NonNegativeReals, RangeSet
from pyomo.environ import Constraint, quicksum, Objective, maximize, ConstraintList
from pyomo.environ import SolverFactory
start_time = time.time()
model = ConcreteModel()

df = pd.read_excel(r'../../inputs/simple_input.xlsx', sheet_name='Sheet1')


# Parameters
Pgmin = df.loc[1:3, 'Unnamed: 1'].tolist()
Pgmax = df.loc[1:3, 'Unnamed: 2'].tolist()
Cg = df.loc[1:3, 'Unnamed: 3'].tolist()
CgUP = df.loc[1:3, 'Unnamed: 4'].tolist()
TgUP = df.loc[1:3, 'Unnamed: 5'].tolist()
TgDN = df.loc[1:3, 'Unnamed: 6'].tolist()
Ug0 = df.loc[1:3, 'Unnamed: 7'].tolist()
HgUP = df.loc[1:3, 'Unnamed: 8'].tolist()
HgDN = df.loc[1:3, 'Unnamed: 9'].tolist()
num_generators = df.loc[1:3, 'GENERATORS'].tolist()
Pdmax = df.loc[7:9, 'Unnamed: 2'].tolist()
Bd = df.loc[7:9, 'Unnamed: 3'].tolist()
num_time_periods = 3

model.G = RangeSet(1, len(num_generators))
model.T = RangeSet(1, num_time_periods)

# Decision Variables
model.p_g = Var(model.G, model.T, within=NonNegativeReals)
model.u_g = Var(model.G, model.T, within=Binary)
model.c_g_UP = Var(model.G, model.T, within=NonNegativeReals)
model.p_d = Var(model.T, within=NonNegativeReals)

# --- Constraints ---

# --- Power Balance Constraint 1 ---
model.power_balance_constraints = ConstraintList()
for t in model.T:
    expr = quicksum(model.p_g[g, t] for g in model.G) - model.p_d[t]
    model.power_balance_constraints.add(expr == 0)

# --- Power Demand Limits Constraint 2 ---
model.demand_constraints = ConstraintList()
for t in model.T:
    # Lower bound
    model.demand_constraints.add(model.p_d[t] >= 0)
    # Upper bound
    model.demand_constraints.add(model.p_d[t] <= Pdmax[t - 1])

# --- Power Produced Limits Constraint 3 ---
model.gen_constraints = ConstraintList()
for g in model.G:
    for t in model.T:
        # Upper bound
        model.gen_constraints.add(model.p_g[g, t] <= Pgmax[g - 1] * model.u_g[g, t])
        # Lower bound
        model.gen_constraints.add(model.p_g[g, t] >= 0)
# --- Power Produced Limits Constraint 4 ---
model.min_stable_gen_constraints = ConstraintList()
for g in model.G:
    for t in model.T:
        model.min_stable_gen_constraints.add(model.p_g[g, t] >= Pgmin[g - 1] * model.u_g[g, t])

# --- Startup Cost Non-negativity Constraint 5 ---
model.startup_constraints = ConstraintList()
for g in model.G:
    for t in model.T:
        model.startup_constraints.add(model.c_g_UP[g, t] >= 0)
# --- Startup Cost bounds Constraint 6 ---
model.startup_constraints = ConstraintList()
for g in model.G:
    for t in model.T:
        if t == 1:
            model.startup_constraints.add(
                model.c_g_UP[g, t] >= (model.u_g[g, t] - Ug0[g - 1]) * CgUP[g - 1])
        else:
            model.startup_constraints.add(
                model.c_g_UP[g, t] >= (model.u_g[g, t] - model.u_g[g, t - 1]) * CgUP[g - 1])

# ---  Minimum Down Time Constraint 7 ---
model.must_stop_constraints = ConstraintList()
for g in model.G:
    for t in model.T:
        if t + TgDN[g - 1] - 1 <= num_time_periods:
            if t > 1:
                expr = sum((1 - model.u_g[g, r]) for r in range(t, t + TgDN[g - 1])) + \
                       TgDN[g - 1] * (model.u_g[g, t] - model.u_g[g, t - 1])
            else:
                expr = sum((1 - model.u_g[g, r]) for r in range(t, t + TgDN[g - 1])) + \
                       TgDN[g - 1] * (model.u_g[g, t] - Ug0[g - 1])

            model.must_stop_constraints.add(expr >= 0)

# ---  Minimum Up Time Constraint 8: ---
model.must_run_constraints = ConstraintList()
for g in model.G:
    for t in model.T:
        if t + TgUP[g - 1] - 1 <= num_time_periods:
            if t > 1:
                expr = sum(model.u_g[g, r] for r in range(t, t + TgUP[g - 1])) - \
                       TgUP[g - 1] * (model.u_g[g, t] - model.u_g[g, t - 1])
            else:
                expr = sum(model.u_g[g, r] for r in range(t, t + TgUP[g - 1])) - \
                       TgUP[g - 1] * (model.u_g[g, t] - Ug0[g - 1])

            model.must_run_constraints.add(expr >= 0)

# ---  Must Run Constraint 9  ---
model.additional_constraints = ConstraintList()
for g in model.G:
    for t in range(num_time_periods - TgUP[g - 1] + 2, num_time_periods + 1):
        if t == 1:
            expr = sum(model.u_g[g, r] - (model.u_g[g, t] - Ug0[g - 1]) for r in range(t, num_time_periods + 1))
        else:
            expr = sum(
                model.u_g[g, r] - (model.u_g[g, t] - model.u_g[g, t - 1]) for r in range(t, num_time_periods + 1))
        model.additional_constraints.add(expr >= 0)

# ---  Must Stop Constraint 10 ---
model.must_stop_additional_constraints = ConstraintList()
for g in model.G:
    t_start = num_time_periods - TgDN[g - 1] + 2
    for t in range(t_start, num_time_periods + 1):
        if t == 1:
            expr = sum(1 - model.u_g[g, r] - (Ug0[g - 1] - model.u_g[g, t]) for r in range(t, num_time_periods + 1))
        else:
            expr = sum(
                1 - model.u_g[g, r] - (model.u_g[g, t - 1] - model.u_g[g, t]) for r in range(t, num_time_periods + 1))
        model.must_stop_additional_constraints.add(expr >= 0)

from pyomo.environ import Objective, maximize, quicksum

# --- Objective Function (SW) ---
model.obj = Objective(
    expr=quicksum(Bd[t - 1] * model.p_d[t] for t in model.T) -
         quicksum(Cg[g - 1] * model.p_g[g, t] for g in model.G for t in model.T) -
         quicksum(model.c_g_UP[g, t] for g in model.G for t in model.T),
    sense=maximize)

# --- Solver ---
solver = SolverFactory('glpk')  # Χρησιμοποιούμε τον GLPK που εγκαταστάθηκε
end_time = time.time()

results = solver.solve(model, tee=True)  # tee=True για να βλέπουμε τα logs του solver

optimal_commitment = {}
for g in model.G:
    for t in model.T:
        optimal_commitment[(g,t)] = int(round(model.u_g[g,t].value))

shadow_prices = {1: 10.0,2: 50.0,3: 10.0}
producer_profit_per_period = {}
for t in model.T:
    total_profit_t = sum(
        shadow_prices[t] * model.p_g[g, t].value -
        (Cg[g-1] * model.p_g[g, t].value + model.c_g_UP[g, t].value)
        for g in model.G
    )
    producer_profit_per_period[t] = total_profit_t

consumer_benefit_per_period = {}
for t in model.T:
    consumer_benefit_per_period[t] = Bd[t-1] * model.p_d[t].value - shadow_prices[t] * model.p_d[t].value

total_producer_profit = sum(producer_profit_per_period.values())
total_consumer_benefit = sum(consumer_benefit_per_period.values())
total_social_welfare = total_producer_profit + total_consumer_benefit

profit_utility_data = []

for t in model.T:
    profit_utility_data.append({
        'Time Period': t,
        'Producers Profit (€)': f"{producer_profit_per_period[t]:.2f} €",
        'Consumers Utility (€)': f"{consumer_benefit_per_period[t]:.2f} €"
    })

profit_utility_data.append({
    'Time Period': 'TOTAL',
    'Producers Profit (€)': f"{total_producer_profit:.2f} €",
    'Consumers Utility (€)': f"{total_consumer_benefit:.2f} €"
})

df_profit_utility = pd.DataFrame(profit_utility_data)

uc_data = []
for g in model.G:
    row = {'Generator': g}
    for t in model.T:
        row[f'Time Period {t}'] = 'ON' if optimal_commitment[(g, t)] > 0 else 'OFF'
    uc_data.append(row)

df_uc = pd.DataFrame(uc_data)
total_execution_time = end_time - start_time

prod_demand_data = []
for t in model.T:
    total_gen = sum(model.p_g[g, t].value for g in model.G)
    total_demand = model.p_d[t].value
    prod_demand_data.append({
        'Time Period': t,
        'Total Generation (MW)': f"{total_gen:.2f} MW",
        'Total Demand (MW)': f"{total_demand:.2f} MW"
    })
df_prod_demand = pd.DataFrame(prod_demand_data)

lmp_data = {f"Time Period {t}": f"{shadow_prices[t]:.2f} €/MW" for t in model.T}
df_lmp = pd.DataFrame([lmp_data])

output_file = r'../../outputs/simple_case_output.xlsx'


with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    df_uc.to_excel(writer, sheet_name='Unit Commitment', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Unit Commitment']
    start_row = len(df_uc) + 2
    worksheet.merge_range(start_row, 0, start_row, len(df_uc.columns) - 1,
                          f"Total Execution Time: {total_execution_time:.4f} s")
    df_prod_demand.to_excel(writer, sheet_name='Production & Demand', index=False)
    df_lmp.to_excel(writer, sheet_name='Production & Demand',
                    index=False, startrow=len(df_prod_demand)+3)
    df_profit_utility.to_excel(writer, sheet_name='Ex-post Summary', index=False)
    worksheet2 = writer.sheets['Ex-post Summary']
    sw_row = len(df_profit_utility) + 2
    df_profit_utility.to_excel(writer, sheet_name='Ex-post Summary', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Ex-post Summary']
    format_black_bold = workbook.add_format({'bold': True, 'font_color': 'black'})
    format_red_bold = workbook.add_format({'bold': True, 'font_color': 'red'})
    sw_row = len(df_profit_utility) + 2
    worksheet.merge_range(sw_row, 0, sw_row, 1, "Total Social Welfare (€)", format_black_bold)
    worksheet.write(sw_row, 2, f"{total_social_welfare:.2f} €", format_red_bold)



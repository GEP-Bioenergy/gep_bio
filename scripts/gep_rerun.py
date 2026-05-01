import os
import logging
import pandas as pd
from math import ceil, pi, exp, log, sqrt, radians, cos, sin, asin
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None

#CONSTANTS
RESULTS_FOLDER = 'results/scenarios'

# MODELLING PARAMETERS
SYSTEM_EFFICIENCY = 0.3 #System efficiency 30%
RESIDUE_PRODUCT_RATIO = 1.48 #RPR
RESIDUE_AVAILABILITY_FACTOR = 0.4 #40% availability
CROP_YIELD = 2.23 #crop yield in tons/ha
ANNUAL_HOURS = 8760
INVESTMENT_COST = 2247 # $/kW
VARIABLE_OM = 0.002 # Variable operations and maintenance  $/kWh
DISCOUNT_RATE = 0.07 #Discount rate 7%
DISCOUNT_FACTOR = 11.65358318 

# Determine NPV of Residue weight (Rt)
def npv_residue(sub_data):
    resArr = sub_data['WeightOfRes'].to_numpy()
    npvResArr = []
    
    # Working out the NPV Res
    for i in range(len(resArr)):
        npvArr = []
        for j in range(26):
            if j == 0:
                npvArr.append(0)
            else:
                npvArr.append(resArr[i])
        npvResArr.append(npf.npv(DISCOUNT_RATE, npvArr))

    sub_data['NpvRes']= npvResArr  
    return sub_data

# Determine NPV of Delivered Fuel cost (Ft)
def npv_fuel_cost_rerun(sub_data):
    sub_data['NpvFt'] = (sub_data['MinimumOverallGenLCOE2030_VOM']*sub_data['NpvGen'])-sub_data['NpvIt']-sub_data['NpvOM']

    # Determining the delivered Fuel cost per Tonne ($/ton)
    sub_data['Ft_PerTonRes'] = sub_data['NpvFt']/sub_data['NpvRes']

    return sub_data

# Cumulative distribution of delivered fuel costs
def fuel_CDF_rerun(sub_data, scenario, fuelCDF):
    DeliveredFuelCost = sub_data['Ft_PerTonRes']
    
    sorted_df = sub_data.sort_values('Ft_PerTonRes')
    
    # Calculate the cumulative proportion of the data that falls below each value
    if len(DeliveredFuelCost) > 0:
        cumulative = np.linspace(0,100, len(DeliveredFuelCost))
        tier = np.array(sorted_df['Tier'])
        print("Length of delivered fuel cost", len(DeliveredFuelCost))
    else:
        cumulative = []
        tier = []
        print("Length of delivered fuel cost",len(DeliveredFuelCost))

    # Sort the data in ascending order
    
    sorted_data = np.sort(DeliveredFuelCost)
    print(type(sorted_data))
    
    # Reassigning index based on length of new dataFrame
    if len(sorted_data) > len(fuelCDF) and len(fuelCDF) != 0:
        
        fuelCDF = fuelCDF.reindex(range(len(sorted_data)))
    
    newCDF = pd.DataFrame({f'{scenario}': sorted_data, f'{scenario}-cum': cumulative, f'{scenario}-tier': tier})
    
    fuelCDF = pd.concat([newCDF, fuelCDF], axis=1)
    
    
    return fuelCDF




# Post processing
def data_postprocessing_rerun(sub_data, scenario, fuelCDF):
    outputName = f'{scenario}-results.csv'

    OUTPUT_DIR = os.getcwd() + f"/{RESULTS_FOLDER}"
    
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    filename = os.path.join(OUTPUT_DIR, outputName)

    sub_data.to_csv(filename, index=False)
    
    fuelCDF.to_csv(os.getcwd() + '/results/CDF.csv', index=False)

    return

# Function assigns Minimum GEN LCOE
def get_gen_lcoe(i, gen_sys, sub_data):
    
    if gen_sys == 'MG_Wind_Hybrid2030':
        return sub_data.WindHybridGenLCOE2030.loc[i]
    
    elif gen_sys == 'MG_PV_Hybrid2030':
        return sub_data.PVHybridGenLCOE2030.loc[i]
    
    elif gen_sys == 'MG_Hydro2030':
        return sub_data.MG_Hydro2030.loc[i]

# Function assigns Minimum GEN LCOE
def get_diesel_con(i, gen_sys, sub_data):
    
    if gen_sys == 'MG_Wind_Hybrid2030':
        return sub_data.WindHybridDieselConsumption2030.loc[i]
    
    elif gen_sys == 'MG_PV_Hybrid2030':
        return sub_data.PVHybridDieselConsumption2030.loc[i]
    

def check_setup(scenario_file):
    fields =["GridCellArea","Admin1","Tier","X_deg","Y_deg","id","Pop2030","TotalEnergyPerCell","MinimumOverall2030","MinimumOverallLCOE2030",              "WindHybridGenLCOE2030", "PVHybridGenLCOE2030", "MG_Hydro2030", "Generation_Capex2030", "Generation_Capex2025",
             "MGDieselFuelCost2030","WindHybridDieselConsumption2030", "PVHybridDieselConsumption2030"]
    
    data_types_conversion_numeric = {
                                    "GridCellArea": np.float16,
                                    "X_deg": np.float16,
                                    "Y_deg": np.float16,
                                    "Pop2030": np.float16,
                                    "MinimumOverallLCOE2030": np.float16,
                                    "Tier": np.int16,
                                    "Admin1": "category",
                                    "MinimumOverall2030": "category"
                                    }
    
    sub_data = pd.read_csv(scenario_file, dtype=data_types_conversion_numeric, skipinitialspace=True, usecols=fields)
    
    # Drop non mini-grids
    sub_data = sub_data.drop(sub_data[(sub_data.MinimumOverall2030 == 'Grid2030') | (sub_data.MinimumOverall2030 == 'SA_PV2030')].index)
    
    sub_data = sub_data.drop(sub_data[(sub_data.MinimumOverall2030 == 'MG_Hydro2030')].index)

    sub_data = sub_data.reset_index().drop(columns = 'index')
    
    sub_data["MinimumOverallGenLCOE2030"] = [ get_gen_lcoe(i, gen_sys, sub_data) for i, gen_sys in enumerate(sub_data["MinimumOverall2030"])]
    
    sub_data["MinOverallDieselCon2030"] = [ get_diesel_con(i, gen_sys, sub_data) for i, gen_sys in enumerate(sub_data["MinimumOverall2030"])]
    
    sub_data['MinimumOverallGenLCOE2030_VOM'] = sub_data['MinimumOverallGenLCOE2030'] - VARIABLE_OM
    
    return sub_data
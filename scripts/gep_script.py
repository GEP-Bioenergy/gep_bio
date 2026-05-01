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


# Function assigns Minimum GEN LCOE
def get_gen_lcoe(i, gen_sys, sub_data):
    
    if gen_sys == 'MG_Wind_Hybrid2030':
        return sub_data.WindHybridGenLCOE2030.loc[i]
    
    elif gen_sys == 'MG_PV_Hybrid2030':
        return sub_data.PVHybridGenLCOE2030.loc[i]
    
    elif gen_sys == 'MG_Hydro2030':
        return sub_data.MG_Hydro2030.loc[i]


# Function takes in scenario files and filter out required variables
def data_setup(scenario_file):
    fields = ["GridCellArea","Admin1","Tier","X_deg","Y_deg","id","Pop2030","TotalEnergyPerCell","MinimumOverall2030","MinimumOverallLCOE2030", "WindHybridGenLCOE2030", "PVHybridGenLCOE2030", "MG_Hydro2030", "Generation_Capex2030"]
    
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
    
    sub_data['MinimumOverallGenLCOE2030_VOM'] = sub_data['MinimumOverallGenLCOE2030'] - VARIABLE_OM
    
    return sub_data


# Sets the capacity factor based on the specified tier level
def get_capacity_factor(tier):
    
    if tier == 1 or tier == 2:
        capacity_factor = (4/24) #Capacity factor (CF)% 4hrs electricity supply daily -> Tier 1,2
    
    elif tier == 3:
        capacity_factor = (8/24) #Capacity factor (CF)% 8hrs electricity supply daily -> Tier 3
    
    elif tier == 4:
        capacity_factor = (16/24) #Capacity factor (CF)% 8hrs electricity supply daily -> Tier 4
    
    elif tier == 5:
        capacity_factor = (23/24) #Capacity factor (CF)% 8hrs electricity supply daily -> Tier 5
        
    return capacity_factor

# Get top crop  
def get_top_crop(state, top_crop):
 
    return top_crop.loc[top_crop['States'] == state, 'Crop'].iloc[0]

# Get Lower Heating Value (MJ/kg)
def get_LHV_crop(crop, crop_data):
    
    return crop_data.loc[crop_data['Crop'] == crop, 'LHV'].iloc[0]

# Get RPR 
def get_RPR_crop(crop, crop_data):
    return crop_data.loc[crop_data['Crop'] == crop, 'RPR'].iloc[0]

# Get Crop Yield value
def get_yield_crop(crop, crop_data):
    
    return crop_data.loc[crop_data['Crop'] == crop, 'CropYield'].iloc[0]

# Get Percentage of Cropping Area value
def get_percentage_area(state, top_crop):
    
    return top_crop.loc[top_crop['States'] == state, 'PercentageArea'].iloc[0]

# Gasifier Capacity 
def gasifier_parameters(sub_data, scenario):
    sub_data['CapFactor'] = [get_capacity_factor(c) for c in sub_data['Tier']]
    
    sub_data['GasifierCap']=sub_data['TotalEnergyPerCell']/(sub_data['CapFactor']*ANNUAL_HOURS*SYSTEM_EFFICIENCY)

    # Determine Gasifier investment cost in $ (CAPEX), using Investment per kW and GasifierCap
    sub_data['investment']=sub_data['GasifierCap'] * INVESTMENT_COST
    
    return sub_data




'''
Analyzing crop demand using agricultural production data and Residue Product Ratio (RPR):
    # Determine the weight of residues in tons
    # Lower heating value in MJ/kg, conversion to tons (1000)
'''
def crop_land_calc(sub_data, top_crop, crop_data):
    
    # Add crop_data to sub_data
    sub_data['TopCrop'] = [ get_top_crop(state, top_crop) for state in sub_data['Admin1']]
    sub_data['PercentageArea'] = [ get_percentage_area(state, top_crop) for state in sub_data['Admin1']]
    
    sub_data['LHV'] = [ get_LHV_crop(crop, crop_data) for crop in sub_data['TopCrop']]
    sub_data['RPR'] = [ get_RPR_crop(crop, crop_data) for crop in sub_data['TopCrop']]
    sub_data['CropYield'] = [ get_yield_crop(crop, crop_data) for crop in sub_data['TopCrop']]
    
    # Calculate residue weight based on top crop LHV
    sub_data['WeightOfRes']= (sub_data['TotalEnergyPerCell']* 3.6)/(0.3 * sub_data['LHV'] * 1000) #Ton 
    
    # Determine the weight of needed product (tons) @40% Availability
    sub_data['WeightOfProd40']=sub_data['WeightOfRes']/(RESIDUE_AVAILABILITY_FACTOR* sub_data['RPR'])
    
    # Estimate cropping area using yield
    sub_data['CropLandArea']=sub_data['WeightOfProd40']/(sub_data['CropYield']) #ha
    
    # Estimate cropping area based on cultivation percentage of TopCrop
    sub_data['CultivationArea']=sub_data['CropLandArea']/(sub_data['PercentageArea']) #ha
    
    return sub_data


'''
1.6. Determine the competitive cost for residues
        
        NPV(Ft)=  (LCOE* NPV(Et))-NPV(It)-NPV(O&Mt)
'''
# Determine NPV of Investment cost (It)
def npv_investment(sub_data):
    investArr = sub_data['investment'].to_numpy()
    npvInvestmentArr = []

    # Working out NPV(It)
    for i in range(len(investArr)):
        npvArr = []
        for j in range(26):
            if j == 1:
                npvArr.append(investArr[i])
            else:
                npvArr.append(0)
        npvInvestmentArr.append(npf.npv(DISCOUNT_RATE, npvArr))
        
    sub_data['NpvIt']= npvInvestmentArr
    return sub_data

# Determine NPV Generation (Et)
def npv_generation(sub_data):
    genArr = sub_data['TotalEnergyPerCell'].to_numpy()
    npvGenArr = []
    
    # Working out the NPV Gen
    for i in range(len(genArr)):
        npvArr = []
        for j in range(26):
            if j == 0:
                npvArr.append(0)
            else:
                npvArr.append(genArr[i])
        npvGenArr.append(npf.npv(DISCOUNT_RATE, npvArr))

    sub_data['NpvGen']= npvGenArr  
    return sub_data

# Determine NPV Operations and Maintenance (O&Mt) at 5% (0.05) of investment cost
def npv_operations(sub_data):
    omArr = (sub_data['investment']* 0.05).to_numpy()
    npvOmArr = []
    
    # Working out NPV Operations
    for i in range(len(omArr)):
        npvArr = []
        for j in range(26):
            if j == 0:
                npvArr.append(0)
            else:
                npvArr.append(omArr[i])
        npvOmArr.append(npf.npv(DISCOUNT_RATE, npvArr))

    sub_data['NpvOM']= npvOmArr
    return sub_data

'''
Ft ($)= NPV(Ft)/(∑_(t=1)^n▒1/(1+r)^t)

 where (∑_(t=1)^n▒1/(1+r)^t) is the discount factor
'''
# Determine NPV of Delivered Fuel cost (Ft)
# def npv_fuel_cost(sub_data):
#     sub_data['NpvFt'] = (sub_data['MinimumOverallGenLCOE2030']*sub_data['NpvGen'])-sub_data['NpvIt']-sub_data['NpvOM']
    
#     # Calculating the Delivered Fuel cost ($) annually using the discount factor
#     sub_data['Ft'] = sub_data['NpvFt']/DISCOUNT_FACTOR

#     # Determining the delivered Fuel cost per Tonne ($/ton)
#     sub_data['Ft_PerTonRes'] = sub_data['Ft']/sub_data['WeightOfRes']

#     return sub_data



  
# Cumulative distribution of delivered fuel costs
# def fuel_CDF(sub_data, scenario, fuelCDF):
#     DeliveredFuelCost = sub_data['Ft_PerTonRes']
    
#     sorted_df = sub_data.sort_values('Ft_PerTonRes')
    
#     # Calculate the cumulative proportion of the data that falls below each value
#     if len(DeliveredFuelCost) > 0:
#         cumulative = np.linspace(0,100, len(DeliveredFuelCost))
#         tier = np.array(sorted_df['Tier'])
#         print("Length of delivered fuel cost", len(DeliveredFuelCost))
#     else:
#         cumulative = []
#         tier = []
#         print("Length of delivered fuel cost",len(DeliveredFuelCost))

#     # Sort the data in ascending order
    
#     sorted_data = np.sort(DeliveredFuelCost)
#     print(type(sorted_data))
    
#     # Reassigning index based on length of new dataFrame
#     if len(sorted_data) > len(fuelCDF) and len(fuelCDF) != 0:
        
#         fuelCDF = fuelCDF.reindex(range(len(sorted_data)))
    
#     newCDF = pd.DataFrame({f'{scenario}': sorted_data, f'{scenario}-cum': cumulative, f'{scenario}-tier': tier})
    
#     fuelCDF = pd.concat([newCDF, fuelCDF], axis=1)
    
    
#     return fuelCDF


# GEP_Bioenergy
Original GEP-OnSSET analysis on competitive deployment of biomass gasification systems developed based on ``` GEP version 3 ```.

For more details on our methodology and analysis: -> [Bio-Electrification Potential: A Comparative Approach to Assessing Bioenergy Potential in SSA](http://dx.doi.org/10.2139/ssrn.7031778)

### Setup
To reproduce GEP Bio output
- Clone git repository main branch and pip install the required dependencies.
- Create a `/results` folder for GEP Bio output in your root repository.
- Download required country gep scenario results and place in root repository. This can be obtained from [GEP data repository](https://energydata.info/organization/world-bank-grou?q=GEP&sort=score+desc%2C+metadata_modified+desc).
- Specify path to the downloaded gep scenario folder in `GEP_Bio.ipynb` notebook.
- Specify path to crop data file. In our case `/Nigeria_crop.xlsx` 
- Run all cells in the `GEP_Bio.ipynb` notebook to generate GEP Bio output. Each scenario output file would be generated in `/results/scenarios` folder.


### Data
GEP scenario runs and data for different countries can be obtained from [GEP data repository](https://energydata.info/organization/world-bank-grou?q=GEP&sort=score+desc%2C+metadata_modified+desc) or [Official GEP website](https://electrifynow.energydata.info/).

For our case study: [GEP Nigeria](https://energydata.info/dataset/nigeria-global-electrification-platform-gep).



## Structure
### Files
- `GEP_Bio.ipynb`: main notebook file to run GEP scenarios.
- `GEP_bio_analysis.ipynb`: notebook file for plotting and analyzing outputs from GEP Bio model.
- `Nigeria_crop.xlsx`: Contains data on the top energy crop across different states in Nigeria.   

### Folders
- `/scripts`: contains the `gep_script.py` which has all functions used for GEP Bio analysis.
- `/results`: contains all output from running GEP Bio. (NB: this folder needs to be created in the root folder after cloning the repo)

### Variables

Electrification Variables

| Variable | Description | Unit / Notes | Input/Output |
|----------|-------------|--------------|--------------|
| `PerCapitaDemand` | Per capita energy demand | kWh/capita/yr | Input | 
| `Pop2030` | Projected population for the year 2030 | person | Input |
| `HealthDemand2030` | Health sector energy demand in 2030 | kWh/yr | Input |
| `EducationDemand2030` | Education sector energy demand in 2030 | kWh/yr | Input |
| `CommercialDemand2030` | Commercial sector energy demand in 2030 | kWh/yr | Input |
| `AgriDemand2030` | Agricultural energy demand in 2030 | kWh/yr | Input |
| `TotalEnergyPerCell` | Total energy demand in the population cluster | kWh/yr; calculated as: `(Pop2030 * PerCapitaDemand) ± HealthDemand2030 ± EducationDemand2030 ± CommercialDemand2030 ± AgriDemand2030` | Input |
| `MinimumOverall2030` | Least cost electrification technology selected | e.g., mini-grid system | Input |
| `MinimumOverallLCOE2030` | Levelized cost of electrification of the least cost technology | $/kWh | Input |
| `Generation_CAPEX2030` | Estimated generation capital expenditure (investment cost) of least cost technology in 2030 | $ | Input |
| `Generation_CAPEX2025` | Estimated generation capital expenditure (investment cost) of least cost technology in 2025 | $ | Input |
| `X_deg` | Longitude x-coordinates | degrees | Input |
| `Y_deg` | Latitude y-coordinates | degrees | Input |
| `id` | Unique identifier per cluster | — | Input |
| `Tier` | Electricity access tier | — | Input |
| `Admin1` | Location (State/Province) | — | Input |
| `Ft_PerTonRes` | Estimated Feedstock price per ton of residues | $/ton | Output: ` main output from GEP Bio model` |


```

Reference: Gafar, A., Zerriffi, H., Ackom, E., Gergel, S. E., & Mentis, D. (2026). Bio-Electrification Potential: A Comparative Approach to Assessing Bioenergy Potential in Sub-Saharan Africa (SSA).

```
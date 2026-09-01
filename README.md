# GEP_Bioenergy
Original GEP-OnSSET analysis on competitive deployment of biomass gasification systems.

# Data


# Files


## Variables

Electrification Variables

| Variable | Description | Unit / Notes |
|----------|-------------|--------------|
| `PerCapitaDemand` | Per capita energy demand | kWh/capita/yr |
| `Pop2030` | Projected population for the year 2030 | person |
| `HealthDemand2030` | Health sector energy demand in 2030 | kWh/yr |
| `EducationDemand2030` | Education sector energy demand in 2030 | kWh/yr |
| `CommercialDemand2030` | Commercial sector energy demand in 2030 | kWh/yr |
| `AgriDemand2030` | Agricultural energy demand in 2030 | kWh/yr |
| `TotalEnergyPerCell` | Total energy demand in the population cluster | kWh/yr; calculated as: `(Pop2030 * PerCapitaDemand) ± HealthDemand2030 ± EducationDemand2030 ± CommercialDemand2030 ± AgriDemand2030` |
| `MinimumOverall2030` | Least cost electrification technology selected | e.g., mini-grid system |
| `MinimumOverallLCOE2030` | Levelized cost of electrification of the least cost technology | $/kWh |
| `Generation_CAPEX2030` | Estimated generation capital expenditure (investment cost) of least cost technology in 2030 | $ |
| `Generation_CAPEX2025` | Estimated generation capital expenditure (investment cost) of least cost technology in 2025 | $ |
| `X_deg` | Longitude x-coordinates | degrees |
| `Y_deg` | Latitude y-coordinates | degrees |
| `id` | Unique identifier per cluster | — |
| `Tier` | Electricity access tier | — |
| `Admin1` | Location (State/Province) | — |

full description of variables can be found in [Energydata.info](https://energydata.info/dataset/nigeria-global-electrification-platform-gep/resource/03b176b5-4430-4957-bdf2-fd973127f5fa)


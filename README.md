# ESG Anayltics


## Purpose of this notebook and visualization

This notebook is created to visualize the carbon emissions produced by a textile manufacturing company across all of their 7 sites across 12 monhts of 2024.

## Dataset Origin

This dataset was obtained from https://topmate.io/arpit_sharma16. The Dataset was built using extensive research from authentic textile industry benchmarks and standards.


## About the Dataset

It includes Scope1, Scope2 and Scope3 emission data for all sites in the company. We have visualized only Scope1 and Scope2 emissions for this project. 
Sites Covered include : 
1. 5 Manyfacturing sites -  M1 to M5  with varying capacities, large, medium and small
2. 1 Office Facility - O1 (2000 M^2)
3. 1 warehourse  - W1 (5000 M^2)


### Data dictionary 

| Column Name | Data Type | Non-Null Count | Missing Count | Missing (%) | Unique Values | Sample Values | Description |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **Site Name** | `object` | 228 | 0 | 0.0 | 7 | `[M-1, M-2, M-3]` | |
| **Year** | `int64` | 228 | 0 | 0.0 | 1 | `[2024]` | |
| **Month** | `object` | 228 | 0 | 0.0 | 12 | `[January, February, March]` | |
| **Scope** | `object` | 228 | 0 | 0.0 | 2 | `[Scope-1, Scope-2]` | |
| **Emission Category** | `object` | 228 | 0 | 0.0 | 2 | `[Fuel Combustion, Purchased Electricity]` | |
| **Emission Source** | `object` | 228 | 0 | 0.0 | 3 | `[Coal, Diesel, Grid Electricity (Location-based)]` | |
| **Activity Value** | `float64` | 228 | 0 | 0.0 | 228 | `[359747.14, 5806.23, 53895.95]` | |
| **Activity Unit** | `object` | 228 | 0 | 0.0 | 3 | `[kg, Liters, kWh]` | |
| **Emission Factor** | `object` | 228 | 0 | 0.0 | 3 | `[2.41 tCO2e/ton, 2.68 kg CO2e/L, 0.727 kg CO2e/kWh]` | |
| **Emission Value (tCO2e)** | `float64` | 0 | 228 | 100.0 | 0 | `[]` | |
| **DEFRA_Emission Value (tCO2e)** | `float64` | 0 | 228 | 100.0 | 0 | `[]` | |
| **Collected By** | `object` | 228 | 0 | 0.0 | 5 | `[Facility Manager, Site Supervisor, Maintenance Team]` | |
| **Evidence Type** | `object` | 228 | 0 | 0.0 | 3 | `[Supplier Invoice, Invoice, Utility Bill]` | |
| **Calculation** | `float64` | 0 | 228 | 100.0 | 0 | `[]` | |
| **Emission Factor Value** | `float64` | 228 | 0 | 0.0 | 3 | `[2.41, 2.68, 0.727]` | |
| **Emission Factor Unit** | `object` | 228 | 0 | 0.0 | 2 | `[tCO2e/ton, kg]` | |
| **Scope Label** | `string` | 228 | 0 | 0.0 | 2 | `[Scope 1, Scope 2]` | |



## Visualization tools used 
- `plotly` for Visualiation 
- `pandas` and `numpy` for data manipulation 
- `streamlit` for dashboard

## Whay did I choose plotly versus Matplotlib ?
`Plotly` is generally better than `Matplotlib` as we need built-in interactivity, modern visual defaults, and effortless web sharing.  
Matplotlib excels at static, print-ready figures, but Plotly can turn charts into a dynamic web application that allow us to explore data directly

**Advantages of plotly**
- plotly charts includes **built-in interactivity** which includes featues like hovering over data points for values, zooming, panning, etc. 
- With Plotly Express, **complex, multi-dimensional charts can be easily generated in a single line of code.** 
- Plotly figures are more sleek and uses **modern styling and better color palettes.**
- **Easy web and dashboard Intehration** as it renders via Javascript.

**Streamlit** was chosen as it lets us (python devs) to turn static data scripts into a sharable interactive web dashboard in minutes without the need for frontend web development skills.


### How is Emission Value calculated.

 Emission value is calculated as  **Activity Value * Emission factor = Emission Value in Metric Tones of CO2e**

 **Emission factor value is based on the source of fuel used (broadly categorzied as Scope 1 and Scope2)

 ## Data Categories Visualized in this notebook

**Energy Consumption**

- Electricity (kWh): Grid consumption across all sites

- Coal (kg): Used in manufacturing for steam boilers and thermal processes

- Diesel (Liters): For DG sets, forklifts, and backup power


## how to run the app in CLI
Open your terminal and run  
"streamlit run esg_dashboard.py"
that should opena browser with the steamlit app
http://localhost:8501/

## public link to dashboard 
https://esg-analytics-seshasayee.streamlit.app/
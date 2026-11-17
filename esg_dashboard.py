from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# Set page configuration and constants
st.set_page_config(page_title="ESG Emissions Dashboard", page_icon="🌿", layout="wide")
EMISSIONS = "Emission Value (tCO2e)"
COLORS = {"Scope 1": "#2563EB", "Scope 2": "#F59E0B", "Scope 3": "#14B8A6"}
px.defaults.template = "plotly_white"


# Load and validate data, Use caching to avoid reloading on every interaction
@st.cache_data
def load_data(source):
    data = pd.read_csv(source)
    data.columns = data.columns.str.strip()
    required = ["Site Name", "Year_Month", "Scope", "Emission Source", EMISSIONS]
    missing = sorted(set(required) - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if data.empty:
        raise ValueError("The CSV contains no records.")
    scope = data["Scope"].astype("string").str.strip().str.extract(
        r"(?i)^(?:scope[\s_-]*)?([123])(?:\.0+)?$", expand=False
    )
    if scope.isna().any():
        raise ValueError(f"Unrecognized Scope values: {data.loc[scope.isna(), 'Scope'].unique().tolist()}")
    data["Scope Label"] = "Scope " + scope
    data["Year_Month"] = pd.to_datetime(data["Year_Month"], format="%Y-%m", errors="raise")
    data[EMISSIONS] = pd.to_numeric(data[EMISSIONS], errors="raise")
    if data[required].isna().any().any():
        raise ValueError("Required columns contain missing values.")
    if not data[EMISSIONS].map(lambda x: float('-inf') < x < float('inf')).all():
        raise ValueError("Emission values must be finite.")
    for col in ["Site Name", "Emission Source"]:
        data[col] = data[col].astype(str).str.strip()
        if data[col].eq("").any():
            raise ValueError(f"Blank labels found in {col}.")
    return data



#title and sidebar
st.title("🌿 ESG Emissions Dashboard")
st.caption("Explore reported emissions by month, site, scope and source.")

with st.sidebar:
    st.header("Data & filters")
    uploaded = st.file_uploader("Upload an ESG CSV (optional)", type=["csv"])

# Load data
try:
    default = (Path(__file__).resolve().parent 
               / "data" 
               /"esg_df_cleaned.csv"
    )
    if uploaded is None and not default.exists():
        st.info("Upload your ESG CSV using the sidebar, or place esg_df_cleaned.csv beside this script.")
        st.stop()
    df = load_data(uploaded if uploaded is not None else default)
except Exception as exc:
    st.error(f"Unable to load data: {exc}")
    st.stop()



#sidebar filters
with st.sidebar:
    months = sorted(df["Year_Month"].dt.strftime("%Y-%m").unique().tolist())
    start_month = st.selectbox("Start month", months, index=0)
    end_month = st.selectbox("End month", months, index=len(months)-1)
    sites = sorted(df["Site Name"].unique().tolist())
    scopes = sorted(df["Scope Label"].unique().tolist())
    sources = sorted(df["Emission Source"].unique().tolist())
    selected_sites = st.multiselect("Sites", sites, default=sites)
    selected_scopes = st.multiselect("Scopes", scopes, default=scopes)
    selected_sources = st.multiselect("Emission sources", sources, default=sources)
    st.caption("All charts and metrics use these filters. Clear a selection to show no matching data.")

if start_month > end_month:
    st.warning("Start month must be before or equal to end month.")
    st.stop()

filtered = df.loc[
    df["Year_Month"].between(pd.Timestamp(start_month), pd.Timestamp(end_month))
    & df["Site Name"].isin(selected_sites)
    & df["Scope Label"].isin(selected_scopes)
    & df["Emission Source"].isin(selected_sources)
].copy()
if filtered.empty:
    st.warning("No records match your filters. Adjust the sidebar selections.")
    st.stop()

# Aggregate data for charts
monthly = filtered.groupby(["Year_Month", "Scope Label"], as_index=False)[EMISSIONS].sum()
site_scope = filtered.groupby(["Site Name", "Scope Label"], as_index=False)[EMISSIONS].sum()
source_totals = filtered.groupby("Emission Source", as_index=False)[EMISSIONS].sum().sort_values(EMISSIONS, ascending=False)
site_totals = filtered.groupby("Site Name")[EMISSIONS].sum().sort_values(ascending=False)


#Create columns for the dashboard metrics and display them as cards

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total emissions (tCO2e)", f"{filtered[EMISSIONS].sum():,.2f}")
c2.metric("Sites with records", filtered["Site Name"].nunique())
c3.metric("Months with records", filtered["Year_Month"].nunique())
c4.metric("Highest-emission site", str(site_totals.index[0]))
st.caption(f"Selected period: {start_month} to {end_month} · {len(filtered):,} matching records")


# Create charts using Plotly Express

#fig1: Monthly emissions by scope (line chart)
fig1 = px.line(monthly.sort_values("Year_Month"), x="Year_Month", y=EMISSIONS,
    color="Scope Label", markers=True, color_discrete_map=COLORS,
    title="1. Monthly Emissions by Scope", labels={"Year_Month": "Month", "Scope Label": "Scope"})
fig1.update_xaxes(dtick="M1", tickformat="%b %Y")
fig1.update_layout(hovermode="x unified")
fig1.update_yaxes(rangemode="tozero", tickformat=",.0f")

#fig2: Emissions by site and scope (stacked bar chart)
fig2 = px.bar(site_scope, x="Site Name", y=EMISSIONS, color="Scope Label", barmode="stack",
    category_orders={"Site Name": site_totals.index.tolist()}, color_discrete_map=COLORS,
    title="2. Emissions by Site and Scope", labels={"Scope Label": "Scope"})
fig2.update_yaxes(tickformat=",.0f")

#fig4: Heatmap of monthly emissions by site (heatmap)
# Preserve absent site-month combinations as gaps rather than assuming zero.
heatmap = filtered.pivot_table(index="Site Name", columns="Year_Month", values=EMISSIONS, aggfunc="sum")
heatmap = heatmap.reindex(index=site_totals.index, columns=pd.date_range(start_month, end_month, freq="MS"))
heatmap.columns = heatmap.columns.strftime("%b %Y")
fig4 = px.imshow(heatmap, aspect="auto", text_auto=",.0f", color_continuous_scale="YlOrRd",
    title="4. Monthly Emissions by Site", labels={"x": "Month", "y": "Site", "color": "tCO2e"})
fig4.update_xaxes(side="bottom")
fig4.update_traces(hoverongaps=False, hovertemplate="Site: %{y}<br>Month: %{x}<br>Emissions: %{z:,.2f} tCO2e<extra></extra>")


# Display charts in two columns and handle the source donut chart separately to check for valid data
left, right = st.columns(2)
with left:
    fig1.update_layout(height=450, legend_title_text="Scope")
    st.plotly_chart(fig1, width="stretch", key="monthly")
with right:
    fig2.update_layout(height=450)
    st.plotly_chart(fig2, width="stretch", key="sites")
left, right = st.columns(2)
with left:
    if (source_totals[EMISSIONS] < 0).any() or source_totals[EMISSIONS].sum() <= 0:
        st.warning("The source donut requires nonnegative totals with a positive sum. Adjust filters to view it.")
    else:
        fig3 = px.pie(source_totals, names="Emission Source", values=EMISSIONS, hole=0.55,
            title="3. Share of Emissions by Source", color_discrete_sequence=px.colors.qualitative.Safe)
        fig3.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>%{value:,.2f} tCO2e<br>%{percent}<extra></extra>")
        fig3.update_layout(height=450, legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig3, width="stretch", key="sources")
with right:
    fig4.update_layout(height=450)
    st.plotly_chart(fig4, width="stretch", key="heatmap")

# Provide a caption and an expander to view the filtered data, along with a download button
st.caption("Heatmap gaps indicate no matching records, not confirmed zero emissions. Totals use reported emission values; emission-factor calculations are not independently validated.")
with st.expander("View filtered data"):
    st.dataframe(filtered, width="stretch", hide_index=True)

# Provide a download button for the filtered data
st.download_button("Download filtered data (CSV)", data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_esg_data.csv", mime="text/csv")

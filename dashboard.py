import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static, st_folium
from dash_plotting import HazardAssetPlot
from itertools import compress

st.set_page_config(page_title="Bangladesh 7-Towns Dashboard")

@st.cache_data
def load_data():
    infra_assets = pd.read_csv(f"data/assets_filtered.csv")
    cities = pd.read_excel("data/coordinates.xlsx")
    return infra_assets, cities

@st.cache_data
def get_plot(filtered_assets, cities, hazard_var):
    m = HazardAssetPlot(infra_assets=filtered_assets, cities=cities, hazard_var=hazard_var)
    return m

infra_assets, cities = load_data()

st.title("7-Towns Dashboard Prototype")

hazard_col, _,  asset_col = st.columns([4, 1, 2])

with hazard_col:
    st.subheader("Hazards")
    hazard_options = ["Coastal flooding","Riverine flooding"]
    hazard = st.selectbox("Hazard Map", hazard_options)

    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.radio("Scenario year", [2030, 2050, 2080], index=1)

    with col2:
        pathway = st.radio("RCP", ["rcp4p5", "rcp8p5"])

    with col3:
        rp = st.select_slider("Return period", [2, 10, 25, 50, 100])

    flood_type = "inunriver" if hazard == "Riverine flooding" else "inuncoast"
    hazard_var = f"{flood_type}__rp00{rp:03d}__{pathway}__{year}"


with asset_col:
    st.subheader("Assets")
    growth = st.checkbox("Markets", value=True)
    edu = st.checkbox("Schools", value=True)
    shelter = st.checkbox("Shelters", value=True)
    health = st.checkbox("Hospitals", value=True)


included_types = list(compress(["edu", "health", "growth", "shelter"], [edu, health, growth, shelter]))
filtered_assets = infra_assets[infra_assets["Type"].isin((included_types))]

m = get_plot(filtered_assets, cities, hazard_var)
folium_static(m)
#return_data = st_folium(m, pixelated=True)

st.write(f"Using {hazard_var} flood map")





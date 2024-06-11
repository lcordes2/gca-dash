import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import folium_static
from dash_plotting import HazardAssetPlot
from itertools import compress

st.set_page_config(page_title="Bangladesh 7-Towns Dashboard")

@st.cache_data
def load_data():
    infra_assets = pd.read_csv(f"data/assets_filtered.csv")
    cities = pd.read_excel("data/coordinates.xlsx")
    return infra_assets, cities

infra_assets, cities = load_data()

title_col, img_col = st.columns([2, 1])

with title_col:
    st.title("7-Towns Dashboard")
with img_col:
    st.image("data/gca_logo.png")


with st.sidebar:
    city_options = ["All cities"] + list(cities["City"].unique())
    center_city = st.selectbox("Center on", city_options)
    st.divider()
    st.subheader("Hazards")
    hazard_options = ["Coastal flooding","River flooding"]
    hazard_help = """
    Coastal flooding: Flooding resulting from storm surges along coastlines \n
    River flooding: Flooding originating from river overflow
    """
    hazard = st.radio("Hazard map", hazard_options, help=hazard_help)

    
    year_help = """
    Year in which the predicted flooding is going to occur
    """
    year = st.radio("Scenario year", [2030, 2050, 2080], help=year_help)

    pathway_help = """
    RCP 4.5: Optimistic climate scenario assuming declining emissions from 2040 to 2100\n
    RCP 8.5: Pessimistic climate scenario assuming steadyily increasing emissions until 2100
    """
    pathway = st.radio("Scenario Pathway", ["RCP 4.5", "RCP 8.5"], help=pathway_help)

    rp_help = """Frequency with which the flooding event will reoccur"""
    rp = st.select_slider("Return period", [2, 10, 25, 50, 100], help=rp_help)

    rcp = "rcp4p5" if pathway == "RCP 4.5" else "rcp8p5"
    flood_type = "inunriver" if hazard == "River flooding" else "inuncoast"
    hazard_var = f"{flood_type}__rp00{rp:03d}__{rcp}__{year}"

    st.divider()

    st.subheader("Assets")
    growth = st.checkbox("Market centres", value=True)
    edu = st.checkbox("Educational institutions", value=True)
    shelter = st.checkbox("Cyclone shelters", value=True)
    health = st.checkbox("Healthcare institutions", value=True)
    fstp = st.checkbox("FSTP Sites", value=True)


included_types = list(compress(["edu", "health", "growth", "shelter", "FSTP Site"], [edu, health, growth, shelter, fstp]))
included_cities = ["City Center", "FSTP Site"] if fstp else ["City Center"]
filtered_assets = infra_assets[infra_assets["Type"].isin((included_types))]
filtered_cities = cities[cities["Type"].isin((included_cities))]
if center_city == "All cities":
    loc = (23.241346102386135, 89.95056152343751)
    zoom = 8
else:
    loc = (
        cities.loc[(cities["Type"] == "City Center") & (cities["City"] == center_city),"Latitude"].iloc[0],
        cities.loc[(cities["Type"] == "City Center") & (cities["City"] == center_city),"Longitude"].iloc[0]
    )
    zoom = 11


tab1, tab2 = st.tabs(["Dashboard", "Background"])

with tab1:

    m = HazardAssetPlot(
        infra_assets=filtered_assets,
        cities=filtered_cities,
        hazard_var=hazard_var,
        location=loc,
        zoom_start=zoom
    )
    folium_static(m)
    # st.write(f"Using {hazard_var} flood map")


with tab2:
    st.markdown("Source code available on [github](https://github.com/lcordes2/gca-dash)")


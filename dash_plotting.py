import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from folium import Map
import numpy as np
import rasterio
import branca.colormap as cm

class HazardAssetPlot(Map):

    def __init__(self, infra_assets, cities, hazard_var, zoom_start=8, location=(22, 90)):
        super().__init__(zoom_start=zoom_start, location=location, attributionControl=0)
        self.radius = 10
        self.centers =cities[cities["Type"] == "City Center"]
        self.assets = pd.concat([cities[["Latitude", "Longitude", "Type", 'City']], infra_assets])
        self.points = list(zip(self.centers["Latitude"], self.centers["Longitude"]))
        with rasterio.open('data/aqueduct/bounds_reference.tif') as src:
            bounds =  src.bounds
        self.overall_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
        self.aqueduct_path = f'data/aqueduct/{hazard_var}.png'

        self.infra_cols = {
            "FSTP Site": "blue",
            "City Center": "red",
            "health": "purple",
            "growth": "green",
            "edu": "beige",
            "shelter": "gray",
        }
        self.infra_labels = {
            "FSTP Site": "FSTP Site",
            "City Center": "City Center",
            "health": "Healthcare Facility",
            "growth": "Market Centre",
            "edu": "Educational Institution",
            "shelter": "Cyclone Shelter",
        }
        self.add_assets()
        self.add_bboxes()
        self.add_hazard_aqueduct()
        self.add_colorbar()
        # self.center_map()


    def center_map(self):
        self.fit_bounds(self.get_bounds(), padding=(30, 30))


    def add_assets(self):
        marker_cluster = MarkerCluster(maxClusterRadius=30, spiderfyOnMaxZoom=True, disableClusteringAtZoom=11).add_to(self)
        for idx, row in self.assets.iterrows():
            popup = row["City"] if row["Type"] == "City Center" else f"{self.infra_labels[row['Type']]}"
            folium.Marker(
                location=(row['Latitude'], row['Longitude']),
                popup=popup,  
                icon=folium.Icon(color=self.infra_cols[row['Type']]),  
                #max_cluster_radius=40,
                disableClusteringAtZoom=100,  
                #spiderfyOnMaxZoom=True
                ).add_to(marker_cluster)


    def add_bboxes(self):
        for _, row in self.centers.iterrows():
            # Draw bbox of 2xradius length around city centers
            lat_offset = (self.radius * 1000) / 111000  # degrees of latitude per meter (approximation)
            lon_offset = lat_offset / np.cos(np.deg2rad(row['Latitude']))  # degrees of longitude per meter

            xmin = row['Longitude'] - lon_offset
            xmax = row['Longitude'] + lon_offset
            ymin = row['Latitude'] - lat_offset
            ymax = row['Latitude'] + lat_offset
            bounds = [(ymin, xmin), (ymax, xmax)]
            bbox = (xmin, ymin, xmax, ymax)

            folium.Rectangle(
                bounds=bounds,
                color='blue',
                fill=False,
            ).add_to(self)

        folium.Rectangle(
            bounds=self.overall_bounds,
            color='black',
            opacity=0.6,
            fill=False,
        ).add_to(self)

    def add_hazard_aqueduct(self):
        folium.raster_layers.ImageOverlay(
            image=self.aqueduct_path,
            bounds=self.overall_bounds,
            opacity=0.7
        ).add_to(self)




    def add_colorbar(self):
        colors = cm.linear.Blues_08.colors
        colormap = cm.LinearColormap(colors, vmin=0, vmax=10)
        colormap.caption = "Predicted level of flooding in meters"
        colormap.add_to(self)
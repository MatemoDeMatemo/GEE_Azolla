import matplotlib
matplotlib.use("TkAgg") # important - bledy bez tego
import matplotlib.pyplot as plt
import geopandas as gpd
from pathlib import Path
import pandas as pd

pd.set_option("display.float_format", "{:.0f}".format) # time format
pd.set_option("display.max_columns", 5)


## Path/Import
path_desktop = Path.home() / "Desktop"

#shp_path = path_desktop / "GEE_Azolla_Materials" / "Test_Shp" / "Azolla_Detections_as_Polygons_0502_2019.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_2602_2019_1" / "Azolla_Detections_as_Polygons_2602_2019_1.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_25-10_05" / "GEE_Azolla_Polygons_2602_2019_9_25-10_05.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_2_months" / "Azolla_Detection_1103_2019_0501.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_2_months" / "Azolla_Detection_1103_2019_2709.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_2_months" / "Azolla_Detection_1103_2019_benchmarkweek_otherclass.shp"
shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_2_months" / "Azolla_Detection_1103_2019_benchmarkweek_otherclass_6bands.shp"

# Load the data
gdf = gpd.read_file(shp_path)

# Sort by time and polygon size
gdf_sorted = gdf.sort_values(by=["system:tim", "count"], ascending= [True, False])
print("gdf_sorted: ", gdf_sorted)

# Change time type
gdf_sorted["date"] = pd.to_datetime(
    gdf_sorted["system:tim"],
    unit="ms"
    ).dt.floor("s")


#### Visualisation ####
# Plot one polygon
first_row = gdf_sorted.iloc[[0]]

first_row.plot()
plt.show()

# Plot 20 polygons
gdf_sorted.iloc[:20].plot()
plt.show()

# Plot A. pixels for each date
daily_sum = gdf_sorted.groupby("date")["count"].sum()

pd.set_option('display.max_rows', None)
print(daily_sum)

daily_sum.plot()
plt.show()

# Plot A. pixels for each month
gdf_sorted_inx = gdf_sorted.set_index("date")
monthly_sum = gdf_sorted_inx["count"].resample("ME").sum()
monthly_sum.plot()

plt.xlabel("Month")
plt.ylabel("Sum of count")
plt.title("Monthly sum of detections")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



#### Heat map ####

from rasterio import features
from affine import Affine
import matplotlib.pyplot as plt
import numpy as np

## Sprawdź czy CRS jest dobry
if gdf_sorted.crs.is_geographic:
    gdf_sorted = gdf_sorted.to_crs(gdf_sorted.estimate_utm_crs())

## Stworz wektor przechowujacy wszystkie daty zdjec
unqdate_vector = gdf_sorted["date"].unique() # zrob vektor z datami

## Stworz pusty raster dla HM, okresl wymiary obszaru
minx, miny, maxx, maxy = gdf_sorted.total_bounds

pixel_size = 20  # jak duzy jest piskel w metrach
width = int(np.ceil((maxx - minx) / pixel_size))
height = int(np.ceil((maxy - miny) / pixel_size))

transform = Affine.translation(minx, maxy) * Affine.scale(pixel_size, -pixel_size)

# Stworz pusty rastr na wyniki
heatmap = np.zeros((height, width), dtype=np.int32)


## Loop: dla kazdego dnia zlacz poligony w jedna mape rastrowa. Dodaj rastr do HM

for day in unqdate_vector:

    gdf_day = gdf_sorted[gdf_sorted["date"] == day] # wybierz dzien
    #print("count", gdf_day["count"].sum())
    gdf_azolla_pix = gdf_day["count"].sum()

    shapes = ((geom, 1) for geom in gdf_day.geometry) # bierze kazdy polygon i daje mu wartosc 1.

    # funkcja zamienia vector na raster
    daily_raster = features.rasterize(
        shapes=shapes, # zbiera wszystkie poligony i sprawia ze kazdy ma wartosc 1
        out_shape=(height, width), # wymiary nowego rastra
        transform=transform,
        merge_alg=features.MergeAlg.replace,  # jesli jakies piksele sie pokrywaja, to je zamien
        all_touched=True
    )

    # Wyswietl wynik jesli > 30k
    if gdf_azolla_pix > 1000:
        plt.imshow(daily_raster, cmap="hot")
        plt.title(f"Daily map for {day}")
        plt.show()

    heatmap += daily_raster # Dodaj do glownego HM

## Wizualizacja HM
plt.figure(figsize=(10, 8))
plt.imshow(heatmap, cmap="hot")
plt.colorbar(label=f"Overlaps ({day})")
plt.title("Daily Heatmap")
plt.show()

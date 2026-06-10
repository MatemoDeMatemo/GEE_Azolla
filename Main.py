import matplotlib
matplotlib.use("TkAgg") # important - bledy bez tego
import matplotlib.pyplot as plt
import geopandas as gpd
from pathlib import Path
import pandas as pd

from collections import defaultdict # sklejanie

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
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_2_months" / "Azolla_Detection_1103_2019_benchmarkweek_otherclass_6bands.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_Folder" / "AV_0318_2025_09.shp"
shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_Folder_WY" / "AV_20_03_2025_18-03_AV_Classifier_B8_B6_B7_B8A_NDVI.shp"

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

# Plot A. max pixels for each month
gdf_sorted_inx = gdf_sorted.set_index("date")
monthly_max = gdf_sorted_inx["count"].resample("ME").max()
monthly_max.plot()

plt.xlabel("Month")
plt.ylabel("Max count")
plt.title("Monthly max of detections")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Plot A. pixels - max value per N days
N_DAYS = 20  # <- tutaj zmieniasz okres

gdf_sorted_inx = gdf_sorted.set_index("date")
rolling_max = gdf_sorted_inx["count"].resample(f"{N_DAYS}D").max()
rolling_max.plot(marker="o", linewidth=1, markersize=4)

plt.xlabel("Date")
plt.ylabel("Max count")
plt.title(f"Max detections every {N_DAYS} days")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#
# ### Heat map ####
#
# from rasterio import features
# from affine import Affine
# import matplotlib.pyplot as plt
# import numpy as np
#
# ## Sprawdź czy CRS jest dobry
# if gdf_sorted.crs.is_geographic:
#     gdf_sorted = gdf_sorted.to_crs(gdf_sorted.estimate_utm_crs())
#
# ## Stworz wektor przechowujacy wszystkie daty zdjec
# unqdate_vector = gdf_sorted["date"].unique() # zrob vektor z datami #########zmiana
#
# gdf_sorted["date_only"] = gdf_sorted["date"].dt.normalize()  # ucina godziny/minuty/sekundy
# unqdate_vector = gdf_sorted["date_only"].unique()
#
# print(unqdate_vector)
# ## Stworz pusty raster dla HM, okresl wymiary obszaru
# minx, miny, maxx, maxy = gdf_sorted.total_bounds
#
# pixel_size = 20  # jak duzy jest piskel w metrach
# width = int(np.ceil((maxx - minx) / pixel_size))
# height = int(np.ceil((maxy - miny) / pixel_size))
#
# transform = Affine.translation(minx, maxy) * Affine.scale(pixel_size, -pixel_size)
#
# # Stworz pusty rastr na wyniki
# heatmap = np.zeros((height, width), dtype=np.int32)
# raster_list = []
#
# for day in unqdate_vector:
#
#     gdf_day = gdf_sorted[gdf_sorted["date"] == day]        # wybor
#     gdf_day = gdf_sorted[gdf_sorted["date_only"] == day]
#     print(pd.to_datetime(day).strftime("%Y-%m-%d"))
#
#     # 🔥 SKLEJANIE POLIGONÓW Z TEGO SAMEGO DNIA
#     merged_geom = gdf_day.geometry.union_all()
#
#     # raster tylko raz
#     daily_combined = features.rasterize(
#         [(merged_geom, 1)],
#         out_shape=(height, width),
#         transform=transform,
#         all_touched=True
#     )
#     print(f"{pd.to_datetime(day).strftime('%Y-%m-%d')} | pixels Azolla: {daily_combined.sum()}")
#
#     # debug
#     if gdf_day["count"].sum() > 10000:
#         plt.imshow(daily_combined, cmap="hot")
#         plt.title(f"Daily merged map for {day}")
#         plt.show()
#
#     # dodanie do globalnej heatmapy
#     heatmap += daily_combined
#
#     day_only = pd.to_datetime(day).date()
#     raster_list.append((day_only, daily_combined))
#
# for day_only, daily_combined in raster_list:
#     print(day_only)
#
#
# # Stwórz DataFrame z dat i sum pikseli
# dates = [day for day, raster in raster_list]
# pixel_sums = [raster.sum() for day, raster in raster_list]
#
# daily_raster_sum = pd.Series(pixel_sums, index=pd.to_datetime(dates))
# daily_raster_sum = daily_raster_sum.sort_index()
#
# print(daily_raster_sum)
#
# # Plot
# daily_raster_sum.plot(marker="o", linewidth=1, markersize=4)
# plt.xlabel("Data")
# plt.ylabel("Liczba pikseli Azolla")
# plt.title("Liczba pikseli Azolla na przestrzeni roku")
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()
#
# ## Wizualizacja HM
# plt.figure(figsize=(10, 8))
# plt.imshow(heatmap, cmap="hot")
# plt.colorbar(label=f"Overlaps ({day})")
# plt.title("Daily Heatmap")
# plt.show()

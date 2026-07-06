import matplotlib
matplotlib.use("TkAgg") # important - bledy bez tego
import matplotlib.pyplot as plt
import geopandas as gpd
from pathlib import Path
import pandas as pd
import matplotlib.dates as mdates

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
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_Folder_WY" / "AV_20_03_2025_18-03_AV_Classifier_B8_B6_B7_B8A_NDVI.shp"
shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_Folder_WY" / "2026-05-08_detect-2025-01-01_to_2026-01-01_clf-AV_Classifier_2026-05-08_n6_B5_B6_B7_B8_B8A_NDVI.geojson"

# Load the data
gdf = gpd.read_file(shp_path)

# Sort by time and polygon size
# gdf_sorted = gdf.sort_values(by=["system:tim", "count"], ascending= [True, False])
# print("gdf_sorted: ", gdf_sorted)
#
# # Change time type
# gdf_sorted["date"] = pd.to_datetime(
#     gdf_sorted["system:tim"],
#     unit="ms"
#     ).dt.floor("s")

# json
# Posortuj cale dane, najpierw po czasie, potem liczbie pixeli na poligon (od najwiekszego)
gdf_sorted = gdf.sort_values(
    by=["system:time_start", "count"],
    ascending=[True, False]
)
print(gdf_sorted)

# Zamiana czasu z ciagu cyfr na daty
gdf_sorted["date"] = pd.to_datetime(
    gdf_sorted["system:time_start"],
    unit="ms"
).dt.floor("s")



### Wykresimport matplotlib.dates as mdates
N_DAYS = 15

gdf_sorted_inx = gdf_sorted.set_index("date")
rolling_max = gdf_sorted_inx["count"].resample(f"{N_DAYS}D").max()

fig, ax = plt.subplots(figsize=(10, 5))

rolling_max.plot(
    ax=ax,
    marker="o",
    linewidth=1.5,
    markersize=4
)

# ---- TUTAJ DODAJ ----

ticks = pd.date_range(
    start="2025-01-01",
    end="2025-12-31",
    freq="MS"
)


ax.set_xticks(ticks)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))

ax.set_xlim(
    pd.Timestamp("2025-01-01"),
    pd.Timestamp("2025-12-31")
)

# ---------------------

ax.set_title(
    f"Maximum detections every {N_DAYS} days",
    fontweight="bold",
    fontsize=14
)

ax.set_xlabel("Date")
ax.set_ylabel("Maximum count")

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

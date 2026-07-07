import matplotlib
matplotlib.use("TkAgg") # important - bledy bez tego
import matplotlib.pyplot as plt
import geopandas as gpd
from pathlib import Path
import pandas as pd
import matplotlib.dates as mdates

pd.set_option("display.float_format", "{:.2f}".format)
pd.set_option("display.max_columns", 5)


## Path/Import
path_desktop = Path.home() / "Desktop"
# File import - zawiera polygony z Azolla z roznych dat. Wiele polygonow dla jednego dnia.
shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_Folder_WY" / "AV_2025_full_year" / "AV_20_03_2025_18-03_AV_Classifier_B8_B6_B7_B8A_NDVI.shp"
#shp_path = path_desktop / "GEE_Azolla_Materials" / "GEE_Folder_WY" / "2026-05-08_detect-2025-01-01_to_2026-01-01_clf-AV_Classifier_2026-05-08_n6_B5_B6_B7_B8_B8A_NDVI.geojson"

# Load the data
gdf = gpd.read_file(shp_path)
print(gdf.columns)

# Sort the polygons
gdf_sorted = gdf.sort_values(
    by=["system:tim", "count"],
    ascending=[True, False]
)

# Change date format
gdf_sorted["date"] = pd.to_datetime(gdf_sorted["system:tim"],unit="ms").dt.floor("s")
gdf_sorted["date_ymd"] = pd.to_datetime(gdf_sorted["system:tim"],unit="ms").dt.date

# Print the polygons
print("gdf_sorted: \n", gdf_sorted[["image_id", "count", "date", "date_ymd"]])

## Group by date

count_per_day = (
    gdf_sorted
    .groupby("date")["count"]
    .sum()
    .reset_index(name="count_sum")
)

count_per_day["hectars"] = count_per_day["count_sum"].astype(float) * 0.01
print("count_per_day: \n", count_per_day)

## Stats by a day

daily_stats = (
    gdf_sorted
    .groupby("date")["count"]
    #.groupby("date_ymd")["count"]
    .agg(
        count_sum="sum",
        n_polygons="count",
        max_polygon="max"
    )
    .reset_index()
)

print(daily_stats.to_string(index=False))



#### Plot 1 - Timescale



### Wykresimport matplotlib.dates as mdates
N_DAYS = 15

count_per_day = count_per_day.set_index("date") # make "date" an index
rolling_max = (
    count_per_day["hectars"]
    .resample(f"{N_DAYS}D")  # divide the data by N_DAYS
    .max()
)
print("rolling_max: \n", rolling_max)
# Fig maker


fig, ax = plt.subplots(figsize=(10, 5))

rolling_max.plot(
    ax=ax,
    marker="o",
    linewidth=1.5,
    markersize=4,
    color="#2E7D32"
)

# główne ticki - pierwszy dzień miesiąca
ticks_month = pd.date_range(
    start="2025-01-01",
    end="2025-12-01",
    freq="MS"
)

# pomocnicze ticki - połowa miesiąca
ticks_mid = pd.to_datetime([
    "2025-01-15",
    "2025-02-15",
    "2025-03-15",
    "2025-04-15",
    "2025-05-15",
    "2025-06-15",
    "2025-07-15",
    "2025-08-15",
    "2025-09-15",
    "2025-10-15",
    "2025-11-15",
    "2025-12-15"
])


# ustaw główne ticki
ax.set_xticks(ticks_month)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

# ustaw pomocnicze ticki
ax.set_xticks(ticks_mid, minor=True)

ax.tick_params(
    axis="x",
    which="minor",
    length=4
)

ax.tick_params(
    axis="x",
    which="major",
    length=7
)


#ax.minorticks_off() # turn off minor ticks
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

ax.set_xlim(
    pd.Timestamp("2025-01-01"),
    pd.Timestamp("2025-12-31")
)

# ---------------------

ax.set_title(
    r"$\it{Azolla\ filiculoides}$ coverage dynamics in the Tagus River (2025)",
    #fontweight="bold",
    fontsize=14
)

ax.set_xlabel("Date")
ax.set_ylabel(r"$\it{Azolla\ filiculoides}$ coverage area (ha)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.grid(
    True,
    linestyle="--",
    alpha=0.3
)

plt.xticks(rotation=0)
ax.set_yticks(range(0, 101, 10))
plt.tight_layout()
plt.show()

## 2 plot
# ustawienie daty jako indeks


count_per_day2 = (
    gdf_sorted
    .groupby("date")["count"]
    .sum()
    .reset_index(name="count_sum")
)
count_per_day2["date_ymd"] = pd.to_datetime(count_per_day2["date"]).dt.date

print("cpr2.1: \n", count_per_day2)

count_per_day2 = (
    count_per_day2
    .groupby("date_ymd")["count_sum"]
    .max()
    .reset_index(name="count_sum")
)
print("cpr2.2: \n", count_per_day2)
count_per_day2 = count_per_day2.set_index("date_ymd")

fig, ax = plt.subplots(figsize=(10, 5))

count_per_day2["count_sum"].plot(
    ax=ax,
    marker="o",
    linewidth=1.5,
    markersize=4
)

ticks = pd.date_range(
    start="2025-01-01",
    end="2025-12-31",
    freq="MS"
)

ax.set_xticks(ticks)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

ax.set_xlim(
    pd.Timestamp("2025-01-01"),
    pd.Timestamp("2025-12-31")
)

ax.set_title(
    "Daily Azolla detections",
    fontweight="bold",
    fontsize=14
)

ax.set_xlabel("Months")
ax.set_ylabel("Count")

plt.xticks(rotation=0)
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



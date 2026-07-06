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
N_DAYS = 15  # <- tutaj zmieniasz okres

gdf_sorted_inx = gdf_sorted.set_index("date")
rolling_max = gdf_sorted_inx["count"].resample(f"{N_DAYS}D").max()
rolling_max.plot(marker="o", linewidth=1, markersize=4)

plt.xlabel("Date")
plt.ylabel("Max count")
plt.title(f"Max detections every {N_DAYS} days")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
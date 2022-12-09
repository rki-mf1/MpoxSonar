import plotly.express as px

# example data for example map
Sample_data = px.data.carshare()

fig = px.scatter_mapbox(
    Sample_data,
    lat="centroid_lat",
    lon="centroid_lon",
    color="peak_hour",
    size="car_hours",
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=15,
    zoom=10,
    mapbox_style="carto-positron",
)

fig.show()
""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

pathways_data = pd.read_csv("pathways_data_geometry.csv")

gdf = gpd.GeoDataFrame(pathways_data, geometry = gpd.points_from_xy(pathways_data.lon, pathways_data.lat))
print(f"Pathways read as geodataframe with shape {gdf.shape}")

#testing using a sample
gdf_sample = gdf.sample(frac = 0.05)

# Read the shapefile into a GeoDataFrame
gdf_shapefile = gpd.read_file("data/UT2023_SignSupports_02-10-2025.shp")
print(f"Shapefile read as geodataframe with shape {gdf_shapefile.shape}")

buffer_distance = 10

buffered_gdf_shapefile = gdf_shapefile.copy()
buffered_gdf_shapefile["geometry"] = gdf_shapefile.geometry.buffer(buffer_distance)

# Create a new GeoSeries to store the 2D points
points_2d = []

# Iterate over the geometries in the GeoDataFrame
for geom in buffered_gdf_shapefile.geometry:
    # Check if the geometry is a Point
    if geom.geom_type == 'Point':
        # Extract x and y coordinates, ignoring z
        x, y, *_ = geom.coords[0]
        # Create a new 2D point
        point_2d = Point(x, y)
        points_2d.append(point_2d)
    else:
        # Handle cases where the geometry is not a point, if necessary
        points_2d.append(None)

buffered_gdf_shapefile['geometry'] = points_2d
print("Geometry converted to 2d points")

buffered_gdf_shapefile_geometry = gpd.GeoDataFrame(buffered_gdf_shapefile, geometry = gpd.points_from_xy(buffered_gdf_shapefile.BEG_LONG, buffered_gdf_shapefile.BEG_LAT))

#testing using a sample
buffered_gdf_shapefile_geometry_sample = buffered_gdf_shapefile_geometry.sample(frac = 0.05)

#matching the crs
print(buffered_gdf_shapefile_geometry_sample.crs)
print(gdf_sample.crs)

gdf_sample.set_crs("EPSG:26912", inplace=True)
print("CRS updated")

try:
    print("starting spatial join")
    inner_df = buffered_gdf_shapefile_geometry_sample.sjoin(gdf_sample, how="inner")
    print("Spatial join completed; writing csv")
    inner_df.to_csv("pathways_sign_dataset.csv", index = False)
except Exception as e:
    print(e)
from geopandas import GeoDataFrame  # For type checking
from numpy import float64


# Used for more explicit typing (rather than having to guess what each float64 means).
X = float64
Y = float64


def get_gdf_centroid(geo_df: GeoDataFrame) -> tuple[X, Y]:
    """
    Get a representative centroid for a GeoDataFrame

    Parameters
    ----------
    geo_df
      The GeoDataFrame to find a centroid for.

    Returns
    -------
    tuple[X,Y]
      A tuple of float64 depicting the x- and y-coordinate of the centroid.
    """
    # From: https://stackoverflow.com/a/70088741
    # FIXME UserWarning: Geometry is in a geographic CRS.
    #  Results from 'centroid' are likely incorrect.
    #  Use 'GeoSeries.to_crs()' to re-project geometries to a projected CRS before this operation.
    centroid = geo_df.dissolve().centroid
    # Extract the x- and y-coordinate from the centroid. `.x` and `.y` are essentially 1x1 matrices.
    # .iloc[0] added to avoid FutureWarning.
    x: float64 = centroid.x.iloc[0]
    y: float64 = centroid.y.iloc[0]
    return x, y

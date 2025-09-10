import geopandas as gpd
import requests

def read_optical_fiber_nodes(simplified=False):
    """Download Brazilian optical fiber nodes data from ITU.
    
    This function downloads and processes optical fiber nodes data from ITU
    (International Telecommunication Union). The data includes information about
    optical fiber infrastructure nodes across Brazil.
    Original source: ITU (International Telecommunication Union)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian optical fiber nodes data
        
    Example
    -------
    >>> from tunned_geobr import read_optical_fiber_nodes
    
    # Read optical fiber nodes data
    >>> nodes = read_optical_fiber_nodes()
    """
    
    url = "https://www.itu.int/en/ITU-D/Technology/SiteAssets/node_brazil_public.geojson"
    
    try:
        # Download and read the GeoJSON file directly
        gdf = gpd.read_file(url)
        gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
        
        if simplified:
            # Keep only the most relevant columns for optical fiber nodes
            # Note: Column names will depend on the actual structure of the ITU data
            columns_to_keep = [
                'geometry'
                # Additional columns will be determined based on the actual data structure
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]

    except Exception as e:
        raise Exception(f"Error downloading optical fiber nodes data: {str(e)}")

    return gdf

if __name__ == "__main__":
    # Example usage
    nodes = read_optical_fiber_nodes(simplified=True)
    print(nodes.head())
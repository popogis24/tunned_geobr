import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_ebas(simplified=False):
    """Download Endemic Bird Areas (EBAs) data.
    
    This function downloads and processes Endemic Bird Areas (EBAs) data. EBAs are 
    regions of the world that contain concentrations of bird species found nowhere else.
    Original source: Global Forest Watch
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Endemic Bird Areas data
        
    Example
    -------
    >>> from tunned_geobr import read_ebas
    
    # Read Endemic Bird Areas data
    >>> ebas = read_ebas()
    """
    
    url = "http://gfw2-data.s3.amazonaws.com/conservation/zip/endemic_bird_areas.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download Endemic Bird Areas data")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'EBA_Name',    # Endemic Bird Area name
                    'EBA_ID',      # Endemic Bird Area ID
                    'Area_km2',    # Area in square kilometers
                    'Priority',    # Conservation priority
                    'Region',      # Geographic region
                    'Country'      # Country
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading Endemic Bird Areas data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_ebas()

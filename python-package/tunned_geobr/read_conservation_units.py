import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_conservation_units(simplified=False):
    """Download Conservation Units data from MMA.
    
    This function downloads and processes conservation units data from MMA. 
    The data includes information about conservation units across Brazil.
    Original source: MMA
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with conservation units data
        
    Example
    -------
    >>> from tunned_geobr import read_conservation_units
    
    # Read conservation units data
    >>> conservation_units = read_conservation_units()
    """
    
    url = "https://dados.mma.gov.br/dataset/44b6dc8a-dc82-4a84-8d95-1b0da7c85dac/resource/20327e02-d4fe-4a1b-bd12-e381ab461d97/download/shp_cnuc_2025_03.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from MMA")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = []
            for root, dirs, files in os.walk(temp_dir):
                shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
            
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            polygon_shp = [path for path in shp_files if 'pontos' not in path]
            gdf = gpd.read_file(polygon_shp[0], encoding='utf8')
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            if simplified:
                # For conservation units, we might not have specific columns to simplify yet.
                # This can be expanded later if needed.
                pass
    
    except Exception as e:
        raise Exception(f"Error downloading conservation units data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    gdf = read_conservation_units()
    print(gdf)
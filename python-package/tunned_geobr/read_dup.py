import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_dup(simplified=False):
    """Download DUP (Diretriz Urbanística Provisória) data from ArcGIS.
    
    This function downloads and processes DUP data from ArcGIS. 
    The data includes information about provisional urban planning guidelines across Brazil.
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with DUP data
        
    Example
    -------
    >>> from tunned_geobr import read_dup
    
    # Read DUP data
    >>> dup = read_dup()
    """
    
    url = "https://www.arcgis.com/sharing/rest/content/items/6c228d808d7548819b51859a8b2a775d/data"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from ArcGIS")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file to dup.gdb folder
            gdb_path = os.path.join(temp_dir, "dup.gdb")
            
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(gdb_path)
            
            # Read the geodatabase
            # List layers in the geodatabase to find the main layer
            try:
                layers = gpd.list_layers(gdb_path)
                if not layers:
                    raise Exception("No layers found in the geodatabase")
                
                # Use the first layer (or you can specify a specific layer name if known)
                layer_name = layers['layer'][0] if 'layer' in layers.columns else layers.iloc[0]['layer']
                gdf = gpd.read_file(gdb_path, layer=layer_name)
                
            except Exception as layer_error:
                # Fallback: try to read without specifying layer
                gdf = gpd.read_file(gdb_path)
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns for DUP data
                # Note: Column names may vary, adjust based on actual data structure
                columns_to_keep = [
                    'geometry',
                    'nome',         # Name
                    'uf',           # State
                    'municipio',    # Municipality
                    'codigo',       # Code
                    'tipo',         # Type
                    'situacao',     # Status
                    'data_criacao', # Creation date
                    'area_ha'       # Area in hectares
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading DUP data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    # Example usage
    dup_data = read_dup(simplified=False)
    print(dup_data.head())
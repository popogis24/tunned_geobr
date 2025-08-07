import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_private_aerodromes(simplified=False):
    """Download Private Aerodromes data from MapBiomas.
    
    This function downloads and processes private aerodromes data from MapBiomas. 
    The data includes information about private airports and aerodromes across Brazil.
    Original source: MapBiomas
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with private aerodromes data
        
    Example
    -------
    >>> from tunned_geobr import read_private_aerodromes
    
    # Read private aerodromes data
    >>> aerodromes = read_private_aerodromes()
    """
    
    url = "https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2023/08/Aerodromos_Privados.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from MapBiomas")
            
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
            gdf = gpd.read_file(shp_files[0])
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'nome',          # Aerodrome name
                    'municipio',     # Municipality
                    'uf',           # State
                    'codigo_oaci',  # ICAO code
                    'altitude',     # Altitude
                    'tipo_uso',     # Usage type
                    'compriment',   # Runway length
                    'largura',      # Runway width
                    'tipo_pista'    # Runway type
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading private aerodromes data: {str(e)}")
        
    return gdf

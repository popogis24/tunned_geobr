import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_waterways(simplified=False):
    """Download Waterways data from SNIRH.
    
    This function downloads and processes waterways data from SNIRH (National Water Resources Information System). 
    The data includes information about navigable waterways across Brazil.
    Original source: SNIRH (Sistema Nacional de Informações sobre Recursos Hídricos)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with waterways data
        
    Example
    -------
    >>> from tunned_geobr import read_waterways
    
    # Read waterways data
    >>> waterways = read_waterways()
    """
    
    url = "https://metadados.snirh.gov.br/geonetwork/srv/api/records/48e26e99-db01-45dc-a270-79f27680167b/attachments/GEOFT_TRECHO_HIDROVIARIO.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from SNIRH")
            
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
                    'nome',            # Waterway name
                    'hidrovia',        # Waterway system
                    'rio',            # River name
                    'situacao',       # Status
                    'extensao_km',    # Length in km
                    'administra',     # Administration
                    'regime',         # Water regime
                    'classifica'      # Classification
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading waterways data: {str(e)}")
        
    return gdf

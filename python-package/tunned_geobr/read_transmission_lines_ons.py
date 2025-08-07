import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_transmission_lines_ons(simplified=False):
    """Download Brazilian Transmission Lines data from ONS.
    
    This function downloads and processes the Brazilian Transmission Lines data
    from ONS (National Electric System Operator).
    Original source: ONS - Operador Nacional do Sistema Elétrico
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian transmission lines data
        
    Example
    -------
    >>> from tunned_geobr import read_transmission_lines_ons
    
    # Read transmission lines data
    >>> transmission_lines = read_transmission_lines_ons()
    """
    
    # The URL provided is a blob URL which might be temporary
    # This is the permanent URL to the ONS data portal
    url = "https://sig.ons.org.br/download/LT_SIN.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download transmission lines data from ONS")
            
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
            
            # Convert to SIRGAS 2000 (EPSG:4674) if not already
            if gdf.crs is None or gdf.crs.to_epsg() != 4674:
                gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns
                # Note: Column names may need adjustment based on actual data
                columns_to_keep = [
                    'geometry',
                    'NOME',        # Line name
                    'TENSAO',      # Voltage
                    'EXTENSAO',    # Length
                    'CIRCUITO',    # Circuit
                    'PROPRIETAR',  # Owner
                    'STATUS'       # Status
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading transmission lines data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_transmission_lines_ons()

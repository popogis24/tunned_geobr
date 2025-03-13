import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_water_bodies_ana(simplified=False):
    """Download Brazilian Water Bodies data from ANA.
    
    This function downloads and processes the Brazilian Water Bodies data
    from ANA (National Water Agency). The data includes lakes, reservoirs, and other water bodies.
    Original source: ANA - Agência Nacional de Águas e Saneamento Básico
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian water bodies data
        
    Example
    -------
    >>> from tunned_geobr import read_water_bodies_ana
    
    # Read water bodies data
    >>> water_bodies = read_water_bodies_ana()
    """
    
    url = "https://metadados.snirh.gov.br/files/7d054e5a-8cc9-403c-9f1a-085fd933610c/geoft_bho_massa_dagua_v2019.zip"

    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download water bodies data from ANA")
            
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
                    'nome',        # Water body name
                    'tipo',        # Type of water body
                    'area_km2',    # Area in square kilometers
                    'cocursodag',  # Water course code
                    'cobacia',     # Basin code
                    'nuareacont',  # Contribution area
                    'nuvolumehm',  # Volume in cubic hectometers
                    'dsoperacao'   # Operation status
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading water bodies data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_water_bodies_ana()

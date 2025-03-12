import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_pan_strategic_areas(simplified=False):
    """Download Strategic Areas data from ICMBio's PAN.
    
    This function downloads and processes the Strategic Areas data from ICMBio's 
    National Action Plans (PAN). These are areas of strategic importance for 
    biodiversity conservation in Brazil.
    Original source: ICMBio - Instituto Chico Mendes de Conservação da Biodiversidade
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with PAN strategic areas data
        
    Example
    -------
    >>> from tunned_geobr import read_pan_strategic_areas
    
    # Read PAN strategic areas data
    >>> strategic_areas = read_pan_strategic_areas()
    """
    
    url = "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows?request=GetFeature&service=WFS&version=1.0.0&typeName=ICMBio:pan_icmbio_areas_estrat_052024_a&outputFormat=SHAPE-ZIP"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download strategic areas data from ICMBio")
            
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
                    'nome',        # Area name
                    'pan',         # PAN name
                    'tipo',        # Type of strategic area
                    'area_km2',    # Area in square kilometers
                    'bioma',       # Biome
                    'uf',          # State
                    'municipio',   # Municipality
                    'importancia', # Importance
                    'descricao'    # Description
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading PAN strategic areas data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_pan_strategic_areas()

import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_vegetation(simplified=False):
    """Download Brazilian Vegetation data from IBGE.
    
    This function downloads and processes the Brazilian Vegetation data at 1:250,000 scale
    from IBGE (Brazilian Institute of Geography and Statistics).
    Original source: IBGE - Instituto Brasileiro de Geografia e Estatística
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian vegetation data
        
    Example
    -------
    >>> from tunned_geobr import read_vegetation
    
    # Read vegetation data
    >>> vegetation = read_vegetation()
    """
    
    url = "https://geoftp.ibge.gov.br/informacoes_ambientais/vegetacao/vetores/escala_250_mil/versao_2023/vege_area.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download vegetation data from IBGE")
            
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
                    'NOME',        # Vegetation name
                    'TIPO',        # Vegetation type
                    'REGIAO',      # Region
                    'BIOMA',       # Biome
                    'AREA_KM2'     # Area in square kilometers
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading vegetation data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_vegetation()

import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_geographic_regions(simplified=False):
    """Download Brazilian Geographic Regions data from IBGE.
    
    This function downloads and processes the Brazilian Geographic Regions data
    from IBGE (Brazilian Institute of Geography and Statistics). The data includes
    the official geographic regions division of Brazil from 2017.
    Original source: IBGE - Instituto Brasileiro de Geografia e Estatística
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian geographic regions data
        
    Example
    -------
    >>> from tunned_geobr import read_geographic_regions
    
    # Read geographic regions data
    >>> regions = read_geographic_regions()
    """
    
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/divisao_regional/divisao_regional_do_brasil/divisao_regional_do_brasil_em_regioes_geograficas_2017/shp/RG2017_regioesgeograficas2017_20180911.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download geographic regions data from IBGE")
            
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
                    'CD_RGGI',     # Immediate Geographic Region Code
                    'NM_RGGI',     # Immediate Geographic Region Name
                    'CD_RGINT',    # Intermediate Geographic Region Code
                    'NM_RGINT',    # Intermediate Geographic Region Name
                    'CD_UF',       # State Code
                    'NM_UF',       # State Name
                    'SIGLA_UF',    # State Abbreviation
                    'AREA_KM2'     # Area in square kilometers
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading geographic regions data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_geographic_regions()

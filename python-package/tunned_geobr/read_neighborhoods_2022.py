import geopandas as gpd
import tempfile
import os
import requests
import subprocess
from io import BytesIO

def read_neighborhoods_2022(simplified=False):
    """Download Brazilian Neighborhoods data from IBGE (2022 Census).
    
    This function downloads and processes the Brazilian Neighborhoods data
    from IBGE (Brazilian Institute of Geography and Statistics) for the 2022 Census.
    Original source: IBGE - Instituto Brasileiro de Geografia e Estatística
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian neighborhoods data
        
    Example
    -------
    >>> from tunned_geobr import read_neighborhoods_2022
    
    # Read neighborhoods data
    >>> neighborhoods = read_neighborhoods_2022()
    """
    
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/bairros/shp/BR/BR_bairros_CD2022.zip"
    
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the zip file to the temporary directory
            zip_file_path = os.path.join(temp_dir, "neighborhoods.zip")
            
            # Download the file
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Failed to download neighborhoods data from IBGE")
                
            # Save the content to a file
            with open(zip_file_path, 'wb') as f:
                f.write(response.content)
            
            # Use unzip command line tool to extract the file (handles more compression methods)
            try:
                subprocess.run(['unzip', '-o', zip_file_path, '-d', temp_dir], 
                              check=True, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Failed to extract zip file: {e.stderr.decode()}")
            
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
                    'CD_BAIRRO',   # Neighborhood Code
                    'NM_BAIRRO',   # Neighborhood Name
                    'CD_MUN',      # Municipality Code
                    'NM_MUN',      # Municipality Name
                    'CD_UF',       # State Code
                    'NM_UF',       # State Name
                    'SIGLA_UF',    # State Abbreviation
                    'AREA_KM2'     # Area in square kilometers
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading neighborhoods data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_neighborhoods_2022()

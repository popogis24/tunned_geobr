import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_geology(simplified=False):
    """Download official geology data from IBGE.
    
    This function downloads and processes geological data from IBGE (Brazilian Institute of Geography and Statistics).
    The data includes geological formations and units at 1:250,000 scale.
    Original source: IBGE
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with geological data
        
    Example
    -------
    >>> from geobr import read_geology
    
    # Read geology data
    >>> geology = read_geology()
    """
    
    url = "https://geoftp.ibge.gov.br/informacoes_ambientais/geologia/levantamento_geologico/vetores/escala_250_mil/versao_2023/geol_area.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from IBGE")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract zip content
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
            
            if simplified:
                # Keep only the most relevant columns
                # Note: These columns are based on typical geological data structure
                # You may want to adjust these based on the actual data
                columns_to_keep = [
                    'geometry',
                    'SIGLA_UNID',  # Unit code
                    'NOME_UNIDA',  # Unit name
                    'HIERARQUIA',  # Hierarchy
                    'IDADE_MAX',   # Maximum age
                    'IDADE_MIN',   # Minimum age
                    'ERRO_MAX',    # Maximum error
                    'ERRO_MIN',    # Minimum error
                    'ORIGEM',      # Origin
                    'LITOTIPO1',   # Main lithotype
                    'LITOTIPO2',   # Secondary lithotype
                ]
                gdf = gdf[columns_to_keep]
    
    except Exception as e:
        raise Exception(f"Error downloading geology data: {str(e)}")
        
    return gdf

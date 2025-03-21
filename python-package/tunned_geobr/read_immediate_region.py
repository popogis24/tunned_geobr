import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_immediate_region(simplified=False):
    """Download official immediate region data from IBGE.
    
    This function downloads and processes immediate region data from IBGE (Brazilian Institute of Geography and Statistics).
    The data includes immediate regions of Brazil for the year 2023.
    Original source: IBGE
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with immediate region data
        
    Example
    -------
    >>> from geobr import read_immediate_region
    
    # Read immediate region data
    >>> immediate_region = read_immediate_region()
    """
    
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/Brasil/BR_RG_Imediatas_2023.zip"
    
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
                # Note: These columns are based on typical immediate region data structure
                # You may want to adjust these based on the actual data
                columns_to_keep = [
                    'geometry',
                    'CD_RGI',  # Immediate region code
                    'NM_RGI',  # Immediate region name
                ]
                gdf = gdf[columns_to_keep]
    
    except Exception as e:
        raise Exception(f"Error downloading immediate region data: {str(e)}")
        
    return gdf

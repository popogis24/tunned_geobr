import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_meso_region(simplified=False):
    """Download official mesoregion data from IBGE.
    
    This function downloads and processes mesoregion data from IBGE (Brazilian Institute of Geography and Statistics).
    The data includes mesoregions of Brazil for the year 2022.
    Original source: IBGE
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with mesoregion data
        
    Example
    -------
    >>> from geobr import read_meso_region
    
    # Read mesoregion data
    >>> meso_region = read_meso_region()
    """
    
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/Brasil/BR/BR_Mesorregioes_2022.zip"
    
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
                # Note: These columns are based on typical mesoregion data structure
                # You may want to adjust these based on the actual data
                columns_to_keep = [
                    'geometry',
                    'CD_MESO',  # Mesoregion code
                    'NM_MESO',  # Mesoregion name
                ]
                gdf = gdf[columns_to_keep]
    
    except Exception as e:
        raise Exception(f"Error downloading mesoregion data: {str(e)}")
        
    return gdf

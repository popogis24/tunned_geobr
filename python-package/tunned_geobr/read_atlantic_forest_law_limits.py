import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_atlantic_forest_law_limits(simplified=False):
    """Download Atlantic Forest Legal Limits data from MMA/IBGE.
    
    This function downloads and processes data about the Atlantic Forest legal limits 
    as defined by Law 11.428/2006. The data is provided by IBGE and MMA (Ministry of Environment).
    Original source: MMA - Ministério do Meio Ambiente
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Atlantic Forest legal limits data
        
    Example
    -------
    >>> from tunned_geobr import read_atlantic_forest_law_limits
    
    # Read Atlantic Forest legal limits data
    >>> limits = read_atlantic_forest_law_limits()
    """
    
    url = "http://antigo.mma.gov.br/estruturas/202/_arquivos/shape_mata_atlantica_ibge_5milhoes_policonica_sirgas2000shp_202.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from MMA")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'NM_TEMA',    # Theme name
                    'NM_REGIAO',  # Region name
                    'AREA_KM2',   # Area in km²
                    'LEI',        # Law reference
                    'FONTE'       # Data source
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading Atlantic Forest legal limits data: {str(e)}")
        
    return gdf

import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_apcb_caatinga(simplified=False):
    """Download Priority Areas for Biodiversity Conservation (APCB) data for the Caatinga region.
    
    This function downloads and processes APCB data from the Ministry of Environment (MMA). 
    The data includes priority areas for biodiversity conservation in the Caatinga region.
    Original source: Ministério do Meio Ambiente (MMA)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Caatinga APCB data
        
    Example
    -------
    >>> from tunned_geobr import read_apcb_caatinga
    
    # Read Caatinga APCB data
    >>> apcb = read_apcb_caatinga()
    """
    
    url = "https://www.gov.br/mma/pt-br/assuntos/biodiversidade-e-biomas/biomas-e-ecossistemas/conservacao-1/areas-prioritarias/arquivos/caatinga.zip"
    
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
            shp_files = []
            for root, dirs, files in os.walk(temp_dir):
                shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
            
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(shp_files[0])
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'Nome',        # Area name
                    'Importanci',  # Importance
                    'Prioridade',  # Priority
                    'Area_km2',    # Area in km²
                    'Oportunida',  # Opportunity
                    'Ameaca'       # Threats
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading Caatinga APCB data: {str(e)}")
        
    return gdf

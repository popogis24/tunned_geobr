import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_geomorphology(simplified=False):
    """Download official geomorphology data from IBGE.
    
    This function downloads and processes geomorphological data from IBGE (Brazilian Institute of Geography and Statistics).
    The data includes geomorphological units and features at 1:250,000 scale.
    Original source: IBGE
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with geomorphological data
        
    Example
    -------
    >>> from geobr import read_geomorphology
    
    # Read geomorphology data
    >>> geomorph = read_geomorphology()
    """
    
    url = "https://geoftp.ibge.gov.br/informacoes_ambientais/geomorfologia/vetores/escala_250_mil/versao_2023/geom_area.zip"
    
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
                # Note: These columns are based on typical geomorphological data structure
                # You may want to adjust these based on the actual data
                columns_to_keep = [
                    'geometry',
                    'COMPART',    # Compartment
                    'MODELADO',   # Landform model
                    'MORFOEST',   # Morphostructure
                    'MORFOLOG',   # Morphology
                    'DECLIVIDA',  # Slope
                    'AMPLIT_A',   # Amplitude
                    'ORDEM_REL',  # Relief order
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading geomorphology data: {str(e)}")
        
    return gdf

import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_federal_highways(simplified=False):
    """Download Federal Highways data from MapBiomas.
    
    This function downloads and processes federal highways data from MapBiomas. 
    The data includes information about federally-managed highways across Brazil.
    Original source: MapBiomas
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with federal highways data
        
    Example
    -------
    >>> from tunned_geobr import read_federal_highways
    
    # Read federal highways data
    >>> highways = read_federal_highways()
    """
    
    url = "https://brasil.mapbiomas.org/wp-content/uploads/sites/4/2023/08/rodovia-federal.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from MapBiomas")
            
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
                    'sigla',        # Highway code (BR-XXX)
                    'uf',           # State
                    'jurisdicao',   # Jurisdiction
                    'superficie',   # Surface type
                    'situacao',     # Status
                    'extensao_km',  # Length in km
                    'tipo_trecho'   # Section type
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading federal highways data: {str(e)}")
        
    return gdf

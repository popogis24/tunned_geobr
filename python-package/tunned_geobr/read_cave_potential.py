import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_cave_potential(simplified=False):
    """Download Cave Occurrence Potential data from ICMBio.
    
    This function downloads and processes data about the potential for cave occurrence 
    across Brazil. The data is based on lithological characteristics and was produced 
    by ICMBio's National Center for Cave Research and Conservation (CECAV).
    Original source: ICMBio - Instituto Chico Mendes de Conservação da Biodiversidade
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with cave occurrence potential data
        Columns:
        - geometry: Geometry of the area
        - METODOLOGI: Methodology used to determine potential
        - GRAU_DE_PO: Potential degree (Very High, High, Medium, Low, Very Low)
        - COUNT: Number of occurrences in the area
        
    Example
    -------
    >>> from tunned_geobr import read_cave_potential
    
    # Read cave potential data
    >>> potential = read_cave_potential()
    """
    
    url = "https://www.gov.br/icmbio/pt-br/assuntos/centros-de-pesquisa/cavernas/publicacoes/mapa-de-potencialidades-de-ocorrencia-de-cavernas-no-brasil/dados-mapa-de-potencialidades-de-ocorrencia-de-cavermas-no-brasil.zip/@@download/file"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from ICMBio")
            
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
                    'GRAU_DE_PO'  # Potential degree
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading cave potential data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_cave_potential()

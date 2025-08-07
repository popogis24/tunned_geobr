import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_indigenous_village(simplified=False):
    """Download Indigenous Villages data from FUNAI.
    
    This function downloads and processes data about indigenous villages (aldeias) in Brazil 
    from FUNAI (Fundação Nacional dos Povos Indígenas). The data includes the point location 
    and basic information about registered indigenous villages.
    Original source: FUNAI - Fundação Nacional dos Povos Indígenas
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with indigenous villages data
        Columns:
        - geometry: Village location (Point)
        - nome_aldeia: Village name
        - terra_indigena: Indigenous Land name
        - municipio_nome: Municipality name
        - uf_sigla: State abbreviation
        - etnia_nome: Ethnicity name
        
    Example
    -------
    >>> from tunned_geobr import read_indigenous_villages
    >>> villages = read_indigenous_villages()
    """
    
    url = "https://geoserver.funai.gov.br/geoserver/Funai/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=Funai:aldeias_pontos&outputFormat=SHAPE-ZIP"
    
    try:
        # Download the zip file with a 60-second timeout
        response = requests.get(url, timeout=60)
        if response.status_code != 200:
            raise Exception(f"Failed to download data from FUNAI. Status code: {response.status_code}")
            
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
                columns_to_keep = ['geometry', 'nome_aldeia', 'terra_indigena', 'municipio_nome', 'uf_sigla', 'etnia_nome']
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading indigenous villages data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_indigenous_villages()
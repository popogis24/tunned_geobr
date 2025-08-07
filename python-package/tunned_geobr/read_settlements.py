import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_settlements(simplified=False):
    """Download official settlements data from INCRA.
    
    This function downloads and processes data about settlements (assentamentos) 
    from INCRA (Instituto Nacional de Colonização e Reforma Agrária).
    Original source: INCRA - Certificação de Imóveis Rurais
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with settlements data
        
    Example
    -------
    >>> from geobr import read_settlements
    
    # Read settlements data
    >>> settlements = read_settlements()
    """
    
    url = "https://certificacao.incra.gov.br/csv_shp/zip/Assentamento%20Brasil.zip"
    
    try:
        # Download the zip file
        # Disable SSL verification due to INCRA's certificate issues
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            raise Exception("Failed to download data from INCRA")
            
        # Suppress the InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
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
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'NOME_PROJE',  # Nome do Projeto de Assentamento
                    'MUNICIPIO',   # Município
                    'UF',          # Estado
                    'AREA_HA',     # Área em hectares
                    'NUM_FAMILI',  # Número de famílias
                    'CAPACIDADE',  # Capacidade de famílias
                    'DT_CRIACAO',  # Data de criação
                    'SITUACAO'     # Situação do assentamento
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading settlements data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    settlements = read_settlements()
    print(settlements)
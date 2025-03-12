import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_sigef_properties(simplified=False):
    """Download Certified Properties data from INCRA's SNCI.
    
    This function downloads and processes certified properties data from INCRA's 
    National Property Certification System (Sistema Nacional de Certificação de Imóveis - SNCI). 
    The data includes information about certified rural properties across Brazil.
    Original source: INCRA (Instituto Nacional de Colonização e Reforma Agrária)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with certified properties data
        
    Example
    -------
    >>> from tunned_geobr import read_snci_properties
    
    # Read certified properties data
    >>> properties = read_snci_properties()
    """
    
    url = "https://certificacao.incra.gov.br/csv_shp/zip/Sigef%20Brasil.zip"
    if 1==1:
        return "Essa camada está muito pesada, baixe manualmente no link: " + url
    try:
        # Download the zip file
        # Disable SSL verification due to INCRA's certificate issues
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            raise Exception("Failed to download data from INCRA")
            
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
                    'parcela',      # Property ID
                    'municipio',    # Municipality
                    'uf',          # State
                    'area_ha',     # Area in hectares
                    'status',      # Certification status
                    'data_cert',   # Certification date
                    'cod_imovel',  # Property code
                    'nome_imov'    # Property name
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading certified properties data: {str(e)}")
        
    return gdf

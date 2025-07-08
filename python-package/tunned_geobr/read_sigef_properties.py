import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time # Import time for potential delays between retries

def read_sigef_properties(simplified=False):
    """Download SIGEF Properties data from INCRA.

    This function downloads and processes rural property data from INCRA's
    SIGEF (Sistema de Gestão Fundiária). The dataset contains information
    about rural properties registered in the SIGEF system across Brazil.

    Original source: INCRA (Instituto Nacional de Colonização e Reforma Agrária)

    Parameters
    ----------
    simplified : bool, default False
        If True, returns a simplified version of the dataset with selected columns.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame with SIGEF properties data.

    Example
    -------
    >>> from tunned_geobr import read_sigef_properties

    # Read SIGEF properties data
    >>> properties = read_sigef_properties()
    """
    
    url = "https://certificacao.incra.gov.br/csv_shp/zip/Sigef%20Brasil.zip"
    
    # Configure retries
    retries = Retry(
        total=5,  # Total number of retries to allow
        backoff_factor=1,  # A backoff factor to apply between attempts (e.g., 1, 2, 4, 8 seconds)
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry on
        allowed_methods={"GET"}, # Only retry GET requests
        raise_on_status=False # Don't raise an exception on failed status codes immediately
    )
    
    # Create a session and mount the adapter with retries
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        # Download the zip file in chunks
        # Disable SSL verification due to INCRA's certificate issues
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Use stream=True to download content in chunks with the session
        response = session.get(url, stream=True, verify=False, timeout=300) # Added a timeout for the request
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = os.path.join(temp_dir, "Sigef Brasil.zip")
            # Write the content to the file
            with open(zip_file_path, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=8192):
                    fd.write(chunk)
            
            # Extract the zip file
            with ZipFile(zip_file_path) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]), use_arrow=True)
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
    
    except requests.exceptions.Timeout:
        raise Exception(f"Download timed out after {300} seconds. The file might be too large or the connection too slow.")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"A connection error occurred during download: {str(e)}. This might be due to network issues or server availability.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"An unexpected request error occurred: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing certified properties data: {str(e)}")
        
    finally:
        session.close() # Ensure the session is closed
        
    return gdf


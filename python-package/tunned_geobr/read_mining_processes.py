import geopandas as gpd
import dask_geopandas as dgpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import urllib3

def read_mining_processes(simplified=False, dask=False, output_path=None):
    """Download official mining process data from ANM (National Mining Agency).
    
    This function downloads and processes mining permit data from Brazil's National Mining Agency (ANM).
    The data includes all mining processes such as research permits, mining concessions, etc.
    Original source: SIGMINE/ANM
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
    dask : bool, by default False
        If True, returns a Dask GeoDataFrame.
    output_path : str or None
        Required if dask=True. Directory to store extracted files.
        
    Returns
    -------
    GeoDataFrame or Dask GeoDataFrame
        Geodataframe with mining process data
        
    Example
    -------
    >>> from geobr import read_mining_processes
    
    # Read mining processes data
    >>> mining = read_mining_processes()
    
    # Read as Dask GeoDataFrame
    >>> mining_dask = read_mining_processes(dask=True, output_path='/path/to/output')
    """
    
    url = "https://app.anm.gov.br/dadosabertos/SIGMINE/PROCESSOS_MINERARIOS/BRASIL.zip"
    
    # Retry strategy
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods={"GET"},
        raise_on_status=False
    )
    
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=retries))
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        response = session.get(url, stream=True, verify=False, timeout=300)
        response.raise_for_status()
        
        if dask:
            if output_path is None:
                raise ValueError("Para usar Dask, você deve fornecer um output_path persistente.")
            os.makedirs(output_path, exist_ok=True)
            zip_path = os.path.join(output_path, "BRASIL.zip")
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            with ZipFile(zip_path) as zip_ref:
                zip_ref.extractall(output_path)

            shp_files = [f for f in os.listdir(output_path) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("Nenhum arquivo .shp encontrado no caminho extraído.")
            
            shp_path = os.path.join(output_path, shp_files[0])
            gdf = dgpd.read_file(shp_path, npartitions=30)

        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "BRASIL.zip")
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                with ZipFile(zip_path) as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
                if not shp_files:
                    raise Exception("Nenhum arquivo .shp encontrado.")
                
                shp_path = os.path.join(temp_dir, shp_files[0])
                gdf = gpd.read_file(shp_path, use_arrow=True)

        if simplified:
            # Keep only the most relevant columns
            columns_to_keep = [
                'geometry',
                'PROCESSO',
                'FASE',
                'NOME',
                'SUBS',
                'USO',
                'UF',
                'AREA_HA'
            ]
            existing_columns = ['geometry'] + [c for c in columns_to_keep[1:] if c in gdf.columns]
            gdf = gdf[existing_columns]

        return gdf

    except requests.exceptions.Timeout:
        raise Exception("Download timed out.")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Erro de conexão: {e}")
    except Exception as e:
        raise Exception(f"Erro ao processar dados de processos minerários: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    gdf = read_mining_processes(dask=True, output_path='/media/nvme1tb/datlaz/saco/auxiliary/temp')
    print(gdf)
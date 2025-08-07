import geopandas as gpd
import requests
from io import BytesIO

def read_ibama_embargoes(simplified=False, verbose=False):
    """Download IBAMA Embargoes data.
    
    This function downloads and processes embargoes data from the Brazilian Institute 
    of Environment and Renewable Natural Resources (IBAMA) through their WFS service.
    Original source: IBAMA SISCOM
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
    verbose : boolean, by default False
        If True, prints detailed information about the download process
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with IBAMA Embargoes data
        
    Example
    -------
    >>> from tunned_geobr import read_ibama_embargoes
    
    # Read IBAMA Embargoes data
    >>> embargoes = read_ibama_embargoes()
    """
    
    url = "https://siscom.ibama.gov.br/geoserver/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=publica:vw_brasil_adm_embargo_a&outputFormat=application/json"
    
    if verbose:
        print("Downloading IBAMA Embargoes data...")
    
    try:
        # Download the JSON data
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download data from IBAMA WFS service. Status code: {response.status_code}")
        
        if verbose:
            print("Data downloaded successfully. Processing...")
            
        # Read the GeoJSON directly from the response content
        gdf = gpd.read_file(BytesIO(response.content))
        
        # Convert to SIRGAS 2000 (EPSG:4674) if needed
        if gdf.crs is None or gdf.crs.to_epsg() != 4674:
            if verbose:
                print(f"Converting CRS from {gdf.crs} to SIRGAS 2000 (EPSG:4674)")
            gdf = gdf.to_crs(4674)
            
        if simplified:
            # Keep only the most relevant columns
            # Adjust these based on the actual columns in the dataset
            columns_to_keep = [
                'geometry',
                'nm_municipio',     # Municipality name
                'sg_uf',            # State abbreviation
                'nm_pessoa',        # Person/entity name
                'nr_cpfcnpj',       # CPF/CNPJ number
                'dt_embargo',       # Embargo date
                'nr_processo',      # Process number
                'nr_termo',         # Term number
                'ar_embargada',     # Embargoed area
                'tp_infracao',      # Infraction type
                'ds_infracao'       # Infraction description
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]
            
            if verbose:
                print(f"Simplified dataset with {len(existing_columns)} columns")
    
    except Exception as e:
        raise Exception(f"Error downloading IBAMA Embargoes data: {str(e)}")
    
    if verbose:
        print(f"Download completed. Returning GeoDataFrame with {len(gdf)} records")
        
    return gdf

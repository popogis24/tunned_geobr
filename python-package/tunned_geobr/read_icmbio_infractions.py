import geopandas as gpd
import requests
from io import BytesIO

def read_icmbio_infractions(simplified=False, verbose=False):
    """Download ICMBio Infraction Notices data.
    
    This function downloads and processes infraction notices data from the Brazilian Institute 
    of Environment and Renewable Natural Resources (ICMBio) through the National Spatial 
    Data Infrastructure (INDE) WFS service.
    Original source: ICMBio via INDE
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
    verbose : boolean, by default False
        If True, prints detailed information about the download process
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with ICMBio Infraction Notices data
        
    Example
    -------
    >>> from tunned_geobr import read_icmbio_infractions
    
    # Read ICMBio Infraction Notices data
    >>> infractions = read_icmbio_infractions()
    """
    
    url = "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=autos_infracao_icmbio&outputFormat=application/json"
    
    if verbose:
        print("Downloading ICMBio Infraction Notices data...")
    
    try:
        # Download the JSON data
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download data from ICMBio WFS service. Status code: {response.status_code}")
        
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
                'MUNICIPIO',       # Municipality
                'UF',              # State
                'DATA_AUTO',       # Infraction date
                'TIPO_INFRA',      # Infraction type
                'AREA_PROTE',      # Protected area
                'VALOR_AUTO',      # Fine value
                'NUM_AUTO'         # Infraction number
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]
            
            if verbose:
                print(f"Simplified dataset with {len(existing_columns)} columns")
    
    except Exception as e:
        raise Exception(f"Error downloading ICMBio Infraction Notices data: {str(e)}")
    
    if verbose:
        print(f"Download completed. Returning GeoDataFrame with {len(gdf)} records")
        
    return gdf

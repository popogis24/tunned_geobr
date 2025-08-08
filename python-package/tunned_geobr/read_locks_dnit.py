import geopandas as gpd
import requests
import json

def read_locks_dnit(simplified=False):
    """Download Locks (Eclusas) data from DNIT.
    
    This function downloads and processes locks (eclusas) data from DNIT. 
    The data includes information about navigation locks across Brazil's waterways.
    Original source: DNIT
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with locks data
        
    Example
    -------
    >>> from tunned_geobr import read_locks_dnit
    
    # Read locks data
    >>> locks = read_locks_dnit()
    """
    
    url = "https://servicos.dnit.gov.br/dnitgeo/geoserver/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=vgeo:daq_eclusas_opr&SRSNAME=EPSG:4674&OUTPUTFORMAT=application/json&CQL_FILTER=INCLUDE"
    
    try:
        # Download the GeoJSON data
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from DNIT")
            
        # Parse JSON response
        geojson_data = response.json()
        
        # Create GeoDataFrame from GeoJSON
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
        
        # Set CRS to SIRGAS 2000 (EPSG:4674) - already in this projection from the request
        gdf.crs = 4674
        
        if simplified:
            # Keep only the most relevant columns for locks data
            # Note: Column names may vary, adjust based on actual data structure
            columns_to_keep = [
                'geometry',
                'nome',           # Lock name
                'uf',             # State
                'municipio',      # Municipality
                'rio',            # River
                'hidrovia',       # Waterway
                'situacao',       # Status
                'tipo',           # Type
                'operadora',      # Operating company
                'largura_m',      # Width in meters
                'comprimento_m',  # Length in meters
                'altura_m',       # Height in meters
                'ano_construcao', # Construction year
                'capacidade'      # Capacity
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading locks data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    # Example usage
    locks_data = read_locks_dnit(simplified=False)
    print(locks_data.head())
    print("Locks data downloaded and processed successfully.")

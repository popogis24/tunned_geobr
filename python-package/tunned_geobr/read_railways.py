import geopandas as gpd
import requests
import json

def read_railways(simplified=False):
    """Download Railways data from DNIT.
    
    This function downloads and processes railways data from DNIT. 
    The data includes information about railway networks across Brazil.
    Original source: DNIT
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with railways data
        
    Example
    -------
    >>> from tunned_geobr import read_railways
    
    # Read railways data
    >>> railways = read_railways()
    """
    
    url = "https://servicos.dnit.gov.br/dnitgeo/geoserver/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=vgeo:vw_dif_ferrovias&SRSNAME=EPSG:4674&OUTPUTFORMAT=application/json&CQL_FILTER=INCLUDE"
    
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
            # Keep only the most relevant columns for railways data
            # Note: Column names may vary, adjust based on actual data structure
            columns_to_keep = [
                'geometry',
                'nome',         # Railway name
                'uf',           # State
                'operadora',    # Operating company
                'situacao',     # Status
                'extensao_km',  # Length in km
                'bitola',       # Track gauge
                'carga',        # Cargo type
                'eletrifica',   # Electrification
                'trecho',       # Section
                'municipio'     # Municipality
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading railways data: {str(e)}")
        
    return gdf
if __name__ == "__main__":
    # Example usage
    railways = read_railways(simplified=False)
    print(railways.head())
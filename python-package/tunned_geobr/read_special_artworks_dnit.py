import geopandas as gpd
import tempfile
import os
import requests
from io import BytesIO
import json

def read_special_artworks_dnit(simplified=False):
    """Download Special Artworks data from DNIT (Departamento Nacional de Infraestrutura de Transportes).
    
    This function downloads and processes special artworks (obras de arte especiais) data from DNIT. 
    The data includes information about bridges, viaducts, and other special engineering structures across Brazil.
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with special artworks data
        
    Example
    -------
    >>> from tunned_geobr import read_special_artworks_dnit
    
    # Read special artworks data
    >>> artworks = read_special_artworks_dnit()
    """
    
    url = "https://servicos.dnit.gov.br/dnitgeo/geoserver/ows?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetFeature&TYPENAMES=vgeo:vw_oae&SRSNAME=EPSG:4674&OUTPUTFORMAT=application/json&CQL_FILTER=INCLUDE"
    
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
            # Keep only the most relevant columns for special artworks data
            # Note: Column names may vary, adjust based on actual data structure
            columns_to_keep = [
                'geometry',
                'nome',           # Artwork name
                'tipo',           # Type (bridge, viaduct, etc.)
                'rodovia',        # Highway
                'uf',             # State
                'municipio',      # Municipality
                'extensao_m',     # Length in meters
                'largura_m',      # Width in meters
                'ano_construcao', # Construction year
                'material',       # Construction material
                'situacao',       # Status
                'km_inicial',     # Initial kilometer
                'km_final',       # Final kilometer
                'obstaculos'      # Obstacles crossed
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading special artworks data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    # Example usage
    artworks_data = read_special_artworks_dnit(simplified=False)
    print(artworks_data.head())
    print("Special artworks data downloaded and processed successfully.")

import geopandas as gpd
import requests
from io import BytesIO

def read_pan_strategic_areas(simplified=False):
    """Download ICMBio's Strategic Areas data.
    
    This function downloads and processes the Strategic Areas data from ICMBio
    (Chico Mendes Institute for Biodiversity Conservation) using their WFS service.
    The data includes strategic areas for biodiversity conservation planning.
    Original source: ICMBio - Instituto Chico Mendes de Conservação da Biodiversidade
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with ICMBio's strategic areas data
        
    Example
    -------
    >>> from tunned_geobr import read_pan_strategic_areas
    
    # Read strategic areas data
    >>> strategic_areas = read_pan_strategic_areas()
    """
    
    url = "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows?request=GetFeature&service=WFS&version=1.0.0&typeName=ICMBio:pan_icmbio_areas_estrat_052024_a&outputFormat=json"
    
    try:
        # Download the GeoJSON data
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download strategic areas data from ICMBio WFS")
            
        # Read the GeoJSON directly into a GeoDataFrame
        gdf = gpd.read_file(BytesIO(response.content))
        
        # Convert to SIRGAS 2000 (EPSG:4674) if not already
        if gdf.crs is None or gdf.crs.to_epsg() != 4674:
            gdf = gdf.to_crs(4674)
        
        if simplified:
            # Keep only the most relevant columns
            # Note: Column names may need adjustment based on actual data
            columns_to_keep = [
                'geometry',
                'nome',          # Area name
                'tipo',          # Type of strategic area
                'bioma',         # Biome
                'uf',            # State
                'area_ha',       # Area in hectares
                'descricao',     # Description
                'importancia',   # Importance
                'data_criacao'   # Creation date
            ]
            
            # Filter columns that actually exist in the dataset
            existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
            gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading strategic areas data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_pan_strategic_areas()

import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_production_fields(simplified=False):
    """Download Brazilian Oil and Gas Production Fields data from ANP.
    
    This function downloads and processes the Brazilian Oil and Gas Production Fields data
    from ANP (National Petroleum Agency).
    Original source: ANP - Agência Nacional do Petróleo, Gás Natural e Biocombustíveis
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian oil and gas production fields data
        
    Example
    -------
    >>> from tunned_geobr import read_production_fields
    
    # Read production fields data
    >>> fields = read_production_fields()
    """
    
    url = "https://gishub.anp.gov.br/geoserver/BD_ANP/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=BD_ANP%3ACAMPOS_PRODUCAO_SIRGAS&maxFeatures=40000&outputFormat=SHAPE-ZIP"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download production fields data from ANP")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = []
            for root, dirs, files in os.walk(temp_dir):
                shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
            
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(shp_files[0])
            
            # Convert to SIRGAS 2000 (EPSG:4674) if not already
            if gdf.crs is None:
                gdf.crs = 4674
            elif gdf.crs.to_epsg() != 4674:
                gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns
                # Note: Column names based on typical ANP data structure
                columns_to_keep = [
                    'geometry',
                    'NOME',        # Field name
                    'OPERADOR',    # Operator
                    'BACIA',       # Basin
                    'AMBIENTE',    # Environment (onshore/offshore)
                    'AREA_KM2'     # Area in square kilometers
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading production fields data: {str(e)}")
    
    return gdf

if __name__ == '__main__':
    read_production_fields()
import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_natural_caves(simplified=False):
    """Download Natural Caves data from ICMBio.
    
    This function downloads and processes natural caves data from ICMBio's WFS service. 
    The data includes registered natural caves across Brazil.
    Original source: ICMBio (Instituto Chico Mendes de Conservação da Biodiversidade)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with natural caves data
        
    Example
    -------
    >>> from tunned_geobr import read_natural_caves
    
    # Read natural caves data
    >>> caves = read_natural_caves()
    """
    
    url = "https://geoservicos.inde.gov.br/geoserver/ICMBio/ows?service=wfs&version=1.3.0&request=GetFeature&TYPENAMES=cavernas_092022_p&SRSNAME=EPSG:4674&OUTPUTFORMAT=shape-zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from ICMBio WFS service")
            
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
            
            # CRS should already be 4674 (SIRGAS 2000) as requested in WFS query
            # but let's ensure it
            if gdf.crs is None or gdf.crs.to_epsg() != 4674:
                gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'nome',          # Cave name
                    'municipio',     # Municipality
                    'uf',           # State
                    'litologia',    # Lithology
                    'desenvolvimento_m',  # Cave development in meters
                    'tipo',         # Type
                    'status'        # Status
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading natural caves data: {str(e)}")
        
    return gdf

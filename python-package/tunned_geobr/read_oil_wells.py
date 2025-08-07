import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_oil_wells(simplified=False):
    """Download Brazilian Oil and Gas Wells data from ANP.
    
    This function downloads and processes the Brazilian Oil and Gas Wells data
    from ANP (National Petroleum Agency).
    Original source: ANP - Agência Nacional do Petróleo, Gás Natural e Biocombustíveis
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian oil and gas wells data
        
    Example
    -------
    >>> from tunned_geobr import read_oil_wells
    
    # Read oil wells data
    >>> wells = read_oil_wells()
    """
    
    url = "https://gishub.anp.gov.br/geoserver/BD_ANP/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=BD_ANP%3APOCOS_SIRGAS&maxFeatures=40000&outputFormat=SHAPE-ZIP"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download oil wells data from ANP")
            
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
                    'NOME',        # Well name
                    'OPERADOR',    # Operator
                    'BACIA',       # Basin
                    'CAMPO',       # Field
                    'SITUACAO',    # Status
                    'CATEGORIA'    # Category
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading oil wells data: {str(e)}")
    
    return gdf

if __name__ == '__main__':
    read_oil_wells()
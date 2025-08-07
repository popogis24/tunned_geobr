import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_archaeological_sites(simplified=False):
    """Download Archaeological Sites data from IPHAN.
    
    This function downloads and processes data about archaeological sites in Brazil 
    from IPHAN (Instituto do Patrimônio Histórico e Artístico Nacional). The data 
    includes location and basic information about registered archaeological sites.
    Original source: IPHAN - Instituto do Patrimônio Histórico e Artístico Nacional
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with archaeological sites data
        Columns:
        - geometry: Site location
        - nome: Site name
        - municipio: Municipality
        - uf: State
        - tipo: Site type
        - exposicao: Exposure type
        - relevancia: Relevance
        - preservacao: Preservation state
        - datacao: Dating
        - artefatos: Artifacts found
        - fonte: Data source
        
    Example
    -------
    >>> from tunned_geobr import read_archaeological_sites
    
    # Read archaeological sites data
    >>> sites = read_archaeological_sites()
    """
    
    url = "http://portal.iphan.gov.br/geoserver/SICG/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=SICG:sitios&maxFeatures=50000&outputFormat=SHAPE-ZIP"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from IPHAN")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            # Print columns for debugging
            print("Available columns:", gdf.columns)
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'nome',       # Site name
                    'municipio',  # Municipality
                    'uf',         # State
                    'tipo',       # Site type
                    'relevancia', # Relevance
                    'preservacao' # Preservation state
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading archaeological sites data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_archaeological_sites()

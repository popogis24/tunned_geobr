import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_rppn(simplified=False):
    """Download Private Natural Heritage Reserves (RPPN) data from ICMBio.
    
    This function downloads and processes data about Private Natural Heritage Reserves 
    (Reservas Particulares do Patrimônio Natural - RPPN) in Brazil. RPPNs are private 
    conservation units created by landowners to protect natural areas on their properties.
    Original source: ICMBio - Instituto Chico Mendes de Conservação da Biodiversidade
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with RPPN data
        Columns:
        - geometry: Geometry of the RPPN
        - nome: RPPN name
        - municipio: Municipality
        - uf: State
        - proprietar: Owner name
        - area_ha: Area in hectares
        - portaria: Ordinance number
        - dt_criacao: Creation date
        - bioma: Biome
        - esfera: Administrative sphere (Federal/State)
        
    Example
    -------
    >>> from tunned_geobr import read_rppn
    
    # Read RPPN data
    >>> rppn = read_rppn()
    """
    
    url = "https://sistemas.icmbio.gov.br/simrppn/publico/rppn/shp/"
    
    # Headers para simular um navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # Download the zip file
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            raise Exception(f"Failed to download data from ICMBio. Status code: {response.status_code}")
            
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
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'nome',       # RPPN name
                    'municipio',  # Municipality
                    'uf',         # State
                    'area_ha',    # Area in hectares
                    'bioma'       # Biome
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading RPPN data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_rppn()

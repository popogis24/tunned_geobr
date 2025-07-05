import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO
import urllib3

def read_quilombola_areas(simplified=False):
    """Download Quilombola Areas data from INCRA.
    
    This function downloads and processes data about Quilombola Areas (Áreas Quilombolas)
    in Brazil. These are territories recognized and titled to remaining quilombo communities.
    Original source: INCRA - Instituto Nacional de Colonização e Reforma Agrária
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Quilombola Areas data
        Columns:
        - geometry: Geometry of the area
        - nome: Area name
        - municipio: Municipality
        - uf: State
        - area_ha: Area in hectares
        - fase: Current phase in the titling process
        - familias: Number of families
        - portaria: Ordinance number
        - decreto: Decree number
        - titulo: Title number
        - data_titulo: Title date
        
    Example
    -------
    >>> from tunned_geobr import read_quilombola_areas
    
    # Read Quilombola Areas data
    >>> quilombos = read_quilombola_areas()
    """
    
    url = "https://certificacao.incra.gov.br/csv_shp/zip/Áreas%20de%20Quilombolas.zip"
    
    try:
        # Download the zip file
        # Disable SSL verification due to INCRA's certificate issues
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            raise Exception("Failed to download data from INCRA")
            
        # Suppress the InsecureRequestWarning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
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
                    'nome',       # Area name
                    'municipio',  # Municipality
                    'uf',        # State
                    'area_ha',   # Area in hectares
                    'fase'       # Current phase
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading Quilombola Areas data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    quilombos = read_quilombola_areas()
    print(quilombos)

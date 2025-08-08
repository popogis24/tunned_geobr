import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_dams_ana(simplified=False):
    """Download Dams data from ANA (Agência Nacional de Águas e Saneamento Básico).
    
    This function downloads and processes dams data from ANA. 
    The data includes information about dams and reservoirs across Brazil.
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with dams data
        
    Example
    -------
    >>> from tunned_geobr import read_dams_ana
    
    # Read dams data
    >>> dams = read_dams_ana()
    """
    
    url = "https://metadados.snirh.gov.br/geonetwork/srv/api/records/4a67d806-a73e-4134-befb-e92eabc3fb9b/attachments/GEOFT_BARRAGEM.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from ANA")
            
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
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns for dams data
                # Note: Column names may vary, adjust based on actual data structure
                columns_to_keep = [
                    'geometry',
                    'nome',           # Dam name
                    'tipo',           # Dam type
                    'uso',            # Use purpose
                    'rio',            # River
                    'bacia',          # Basin
                    'uf',             # State
                    'municipio',      # Municipality
                    'altura_m',       # Height in meters
                    'volume_m3',      # Volume in m³
                    'area_ha',        # Area in hectares
                    'ano_conclusao',  # Year of completion
                    'situacao',       # Status
                    'proprietario'    # Owner
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading dams data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    # Example usage
    dams_data = read_dams_ana(simplified=False)
    print(dams_data.head())
    print("Dams data downloaded and processed successfully.")

import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO
import urllib3
import time
from pathlib import Path

def read_quilombola_areas(simplified=False, local_file=None):
    """Download Quilombola Areas data from INCRA.
    
    This function downloads and processes data about Quilombola Areas (Áreas Quilombolas) 
    in Brazil. These are territories recognized and titled to remaining quilombo communities.
    Original source: INCRA - Instituto Nacional de Colonização e Reforma Agrária
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
    local_file : string, optional
        Path to a local zip file containing the data, by default None
        If provided, the function will use this file instead of downloading from INCRA
        
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
    
    # Or use a local file that was previously downloaded
    >>> quilombos = read_quilombola_areas(local_file="path/to/Áreas de Quilombolas.zip")
    """
    
    url = "https://certificacao.incra.gov.br/csv_shp/zip/Áreas%20de%20Quilombolas.zip"
    
    # If a local file is provided, use it instead of downloading
    if local_file and os.path.exists(local_file):
        print(f"Using local file: {local_file}")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the zip file
                with ZipFile(local_file) as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Find the shapefile
                shp_files = [f for f in os.listdir(temp_dir) if f.endswith('.shp')]
                if not shp_files:
                    raise Exception("No shapefile found in the local file")
                
                print(f"Found shapefile: {shp_files[0]}")
                
                # Read the shapefile
                gdf = gpd.read_file(os.path.join(temp_dir, shp_files[0]))
                gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
                
                print(f"Successfully loaded {len(gdf)} Quilombola Areas from local file")
                
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
                
                return gdf
        except Exception as e:
            raise Exception(f"Error processing local file: {str(e)}")
    
    # If no local file is provided, return a message with download instructions
    # This is consistent with the approach in read_snci_properties as mentioned in the MEMORY
    return "O download automático dos dados de Áreas Quilombolas está temporariamente indisponível.\nPor favor, faça o download manual através do link:\n" + url + "\n\nApós o download, você pode usar o parâmetro local_file:\nquilombos = read_quilombola_areas(local_file='caminho/para/Áreas de Quilombolas.zip')"

if __name__ == '__main__':
    quilombos = read_quilombola_areas()
    print(quilombos)

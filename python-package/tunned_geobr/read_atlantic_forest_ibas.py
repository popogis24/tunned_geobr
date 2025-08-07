import geopandas as gpd
import tempfile
import os
import requests
import patoolib
from zipfile import ZipFile
from io import BytesIO

def read_atlantic_forest_ibas(simplified=False):
    """Download Important Bird Areas (IBAs) data for the Atlantic Forest region.
    
    This function downloads and processes IBAs data from SAVE Brasil. The data includes 
    important areas for bird conservation in the Atlantic Forest region.
    Original source: SAVE Brasil
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Atlantic Forest IBAs data
        
    Example
    -------
    >>> from geobr import read_atlantic_forest_ibas
    
    # Read Atlantic Forest IBAs data
    >>> ibas = read_atlantic_forest_ibas()
    """
    
    url = "https://www.savebrasil.org.br/_files/archives/6d1e48_c03ae9708adf4d978220547eaf173103.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from SAVE Brasil")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # First extract the zip file
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)
            
            subfolder_path = os.path.join(temp_dir, "Shapefiles IBAs Amazônia e Mata Atlântica")
            rar_files = [f for f in os.listdir(subfolder_path) if f.endswith('.rar')]

            if not rar_files:
                raise Exception("No RAR file found in the downloaded data")
            
            # Extract the RAR file using patoolib
            rar_path = os.path.join(subfolder_path, rar_files[0])
            patoolib.extract_archive(rar_path, outdir=temp_dir)
                
            # Path to the Atlantic Forest shapefile directory
            atlantic_dir = os.path.join(subfolder_path, "Mata Atlântica")
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(atlantic_dir) if f.endswith('.shp')]
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(os.path.join(atlantic_dir, shp_files[0]))
            gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns
                # Note: These columns are based on typical IBAs data structure
                # You may want to adjust these based on the actual data
                columns_to_keep = [
                    'geometry',
                    'IBA_NAME',    # IBA name
                    'IBA_CODE',    # IBA code
                    'STATE',       # State
                    'AREA_HA',     # Area in hectares
                    'PRIORITY',    # Conservation priority
                    'THREATS',     # Threats to the area
                    'HABITATS',    # Main habitats
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading Atlantic Forest IBAs data: {str(e)}")
        
    return gdf


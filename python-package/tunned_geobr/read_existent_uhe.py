import geopandas as gpd
import os
import tempfile
import urllib.parse
import requests
import shutil
from zipfile import ZipFile
from pathlib import Path
from io import BytesIO
import warnings
import json

def read_existent_uhe(simplified=False, verbose=False):
    """Download Existing Large Hydroelectric Power Plants (UHE) data from EPE.
    
    This function downloads and processes existing large hydroelectric power plants (UHE) data from EPE 
    (Energy Research Company). The data includes information about existing large hydroelectric 
    power generation projects across Brazil.
    Original source: EPE (Empresa de Pesquisa Energética)
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
    verbose : boolean, by default False
        If True, prints detailed information about the download process

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with existing large hydroelectric power plants data
        
    Example
    -------
    >>> from tunned_geobr import read_existent_uhe
    
    # Read existing large hydroelectric power plants data
    >>> existent_uhe = read_existent_uhe()
    """
    
    # URL for the EPE geoserver
    url = r"https://gisepeprd2.epe.gov.br/arcgis/rest/services/Download_Dados_Webmap_EPE/GPServer/Extract%20Data%20Task/execute?f=json&env%3AoutSR=102100&Layers_to_Clip=%5B%22UHE%20-%20Base%20Existente%22%5D&Area_of_Interest=%7B%22geometryType%22%3A%22esriGeometryPolygon%22%2C%22features%22%3A%5B%7B%22geometry%22%3A%7B%22rings%22%3A%5B%5B%5B-8655251.47456396%2C-4787514.465591563%5D%2C%5B-8655251.47456396%2C1229608.401015912%5D%2C%5B-3508899.2341809804%2C1229608.401015912%5D%2C%5B-3508899.2341809804%2C-4787514.465591563%5D%2C%5B-8655251.47456396%2C-4787514.465591563%5D%5D%5D%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D%7D%5D%2C%22sr%22%3A%7B%22wkid%22%3A102100%7D%7D&Feature_Format=Shapefile%20-%20SHP%20-%20.shp&Raster_Format=Tagged%20Image%20File%20Format%20-%20TIFF%20-%20.tif"
 
    try:
        # Disable SSL verification warning
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        if verbose:
            print("Requesting data from EPE server...")
            
        response = requests.get(url, timeout=60, verify=False)
        if not response.ok:
            raise Exception(f"Error getting JSON response: {response.status_code}")

        json_response = response.json()
        
        if verbose:
            print(f"JSON response received: {json.dumps(json_response, indent=2)[:500]}...")
            
        if 'results' not in json_response or len(json_response['results']) == 0:
            raise Exception("Invalid JSON response structure")
            
        if 'value' not in json_response['results'][0] or 'url' not in json_response['results'][0]['value']:
            raise Exception("URL not found in JSON response")
            
        file_url = json_response['results'][0]['value']['url']
        
        if verbose:
            print(f"Downloading file from: {file_url}")
        
        file_response = requests.get(file_url, stream=True, timeout=60, verify=False)
        if not file_response.ok:
            raise Exception(f"Error downloading file: {file_response.status_code}")
        
        # Check if content is actually a zip file
        content = file_response.content
        if len(content) < 100:
            if verbose:
                print(f"Warning: Downloaded content is very small ({len(content)} bytes)")
                print(f"Content preview: {content[:100]}")
            
        # Create a temporary directory to extract the files
        with tempfile.TemporaryDirectory() as temp_dir:
            if verbose:
                print(f"Extracting files to temporary directory: {temp_dir}")
                
            try:
                # Extract the zip file
                with ZipFile(BytesIO(content)) as zip_ref:
                    zip_ref.extractall(temp_dir)
                    
                    if verbose:
                        print(f"Files in zip: {zip_ref.namelist()}")
            except Exception as zip_error:
                if verbose:
                    print(f"Error extracting zip: {str(zip_error)}")
                    print(f"Saving content to debug.zip for inspection")
                    with open("debug.zip", "wb") as f:
                        f.write(content)
                raise Exception(f"Failed to extract zip file: {str(zip_error)}")
            
            # Find the shapefile
            all_files = os.listdir(temp_dir)
            if verbose:
                print(f"Files in temp directory: {all_files}")
                
            shp_files = [f for f in all_files if f.endswith('.shp')]
            if not shp_files:
                # Try looking in subdirectories
                for root, dirs, files in os.walk(temp_dir):
                    shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
                
                if not shp_files:
                    raise Exception("No shapefile found in the downloaded data")
            
            # Read the shapefile
            shp_path = shp_files[0] if os.path.isabs(shp_files[0]) else os.path.join(temp_dir, shp_files[0])
            if verbose:
                print(f"Reading shapefile: {shp_path}")
                
            gdf = gpd.read_file(shp_path)
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            gdf = gdf.to_crs(4674)
            
            if verbose:
                print(f"Data loaded successfully with {len(gdf)} records")
                print(f"Columns: {gdf.columns.tolist()}")
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'nome',            # Power plant name
                    'potencia',        # Capacity in MW
                    'rio',             # River name
                    'bacia',           # Basin
                    'sub_bacia',       # Sub-basin
                    'uf',              # State
                    'municipio',       # Municipality
                    'situacao'         # Status
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                if len(existing_columns) <= 1:
                    if verbose:
                        print("Warning: No matching columns found for simplified version. Returning all columns.")
                else:
                    gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading or processing existing large hydroelectric power plants data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    try:
        uhe_data = read_existent_uhe(verbose=True)
        print(f"Downloaded existing large hydroelectric power plants data with {len(uhe_data)} records and {len(uhe_data.columns)} columns")
        
        # Test simplified version
        simplified_data = read_existent_uhe(simplified=True)
        print(f"Simplified data has {len(simplified_data.columns)} columns: {simplified_data.columns.tolist()}")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

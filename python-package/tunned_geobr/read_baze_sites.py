import geopandas as gpd
import tempfile
import os
import requests
import subprocess
import platform
import shutil
from io import BytesIO

def read_baze_sites(simplified=False):
    """Download Brazilian BAZE Sites data from MMA.
    
    This function downloads and processes the Brazilian BAZE Sites data
    (Sites of Biological Importance and Ecosystem Services) from the
    Ministry of Environment (MMA).
    Original source: MMA - Ministério do Meio Ambiente
    
    Note: This function requires either 'unrar' or 'unar' to be installed on your system
    to extract the RAR file. If you don't have these tools installed, you'll need to 
    install them:
    - On macOS: brew install unrar or brew install unar
    - On Ubuntu/Debian: sudo apt-get install unrar or sudo apt-get install unar
    - On Windows: Install WinRAR or 7-Zip
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian BAZE Sites data
        
    Example
    -------
    >>> from tunned_geobr import read_baze_sites
    
    # Read BAZE Sites data
    >>> baze_sites = read_baze_sites()
    """
    
    url = "http://antigo.mma.gov.br/images/arquivo/80046/Especies/SitiosBAZE_2018.rar"
    
    # Check if extraction tools are available
    unrar_available = shutil.which('unrar') is not None
    unar_available = shutil.which('unar') is not None
    seven_zip_available = shutil.which('7z') is not None
    
    if not (unrar_available or unar_available or seven_zip_available):
        os_name = platform.system()
        if os_name == 'Darwin':  # macOS
            install_msg = "Install with: brew install unrar or brew install unar"
        elif os_name == 'Linux':
            install_msg = "Install with: sudo apt-get install unrar or sudo apt-get install unar"
        elif os_name == 'Windows':
            install_msg = "Install WinRAR or 7-Zip"
        else:
            install_msg = "Install unrar, unar, or 7-Zip"
            
        raise Exception(f"No RAR extraction tool found. This function requires unrar, unar, or 7-Zip to extract the data. {install_msg}")
    
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the RAR file to the temporary directory
            rar_file_path = os.path.join(temp_dir, "baze_sites.rar")
            
            # Download the file
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception("Failed to download BAZE Sites data from MMA")
                
            # Save the content to a file
            with open(rar_file_path, 'wb') as f:
                f.write(response.content)
            
            # Extract the RAR file using available tools
            extraction_success = False
            extraction_error = ""
            
            if unrar_available:
                try:
                    subprocess.run(['unrar', 'x', rar_file_path, temp_dir], 
                                  check=True, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
                    extraction_success = True
                except subprocess.CalledProcessError as e:
                    extraction_error += f"unrar failed: {e.stderr.decode()}. "
            
            if not extraction_success and unar_available:
                try:
                    subprocess.run(['unar', '-d', rar_file_path, '-o', temp_dir], 
                                  check=True, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
                    extraction_success = True
                except subprocess.CalledProcessError as e:
                    extraction_error += f"unar failed: {e.stderr.decode()}. "
            
            if not extraction_success and seven_zip_available:
                try:
                    subprocess.run(['7z', 'x', rar_file_path, f'-o{temp_dir}'], 
                                  check=True, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
                    extraction_success = True
                except subprocess.CalledProcessError as e:
                    extraction_error += f"7z failed: {e.stderr.decode()}. "
            
            if not extraction_success:
                raise Exception(f"Failed to extract RAR file: {extraction_error}")
            
            # Find the shapefile
            shp_files = []
            for root, dirs, files in os.walk(temp_dir):
                shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
            
            if not shp_files:
                raise Exception("No shapefile found in the downloaded data")
                
            # Read the shapefile
            gdf = gpd.read_file(shp_files[0])
            
            # Convert to SIRGAS 2000 (EPSG:4674) if not already
            if gdf.crs is None or gdf.crs.to_epsg() != 4674:
                gdf = gdf.to_crs(4674)
            
            if simplified:
                # Keep only the most relevant columns
                # Note: Column names may need adjustment based on actual data
                columns_to_keep = [
                    'geometry',
                    'nome',        # Site name
                    'categoria',   # Category
                    'area_km2',    # Area in square kilometers
                    'bioma',       # Biome
                    'uf',          # State
                    'importancia', # Importance
                    'descricao',   # Description
                    'referencia'   # Reference
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading BAZE Sites data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_baze_sites()

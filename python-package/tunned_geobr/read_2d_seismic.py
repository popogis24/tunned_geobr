import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_2d_seismic(simplified=False):
    """Download 2D Seismic data from ANP (Agência Nacional do Petróleo).
    
    This function downloads and processes 2D seismic survey data from ANP. 
    The data includes information about 2D seismic surveys conducted for oil and gas exploration across Brazil.
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with 2D seismic survey data
        
    Example
    -------
    >>> from tunned_geobr import read_2d_seismic
    
    # Read 2D seismic data
    >>> seismic_2d = read_2d_seismic()
    """
    
    url = "https://geomaps.anp.gov.br/geoserver/wfs?service=wfs&version=1.0.0&request=GetFeature&typeName=geoanp:seismic2D_all&outputFormat=SHAPE-ZIP&format_options=filename:S%C3%ADsmica%202D-zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from ANP")
            
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
                # Keep only the most relevant columns for 2D seismic data
                # Note: Column names may vary, adjust based on actual data structure
                columns_to_keep = [
                    'geometry',
                    'nome',         # Survey name
                    'operadora',    # Operating company
                    'ano',          # Year
                    'bacia',        # Basin
                    'bloco',        # Block
                    'poco',         # Well
                    'status',       # Status
                    'tipo',         # Type
                    'comprimento',  # Length
                    'data_inicio',  # Start date
                    'data_fim'      # End date
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading 2D seismic data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    # Example usage
    seismic_2d_data = read_2d_seismic(simplified=False)
    print(seismic_2d_data.head())
    print("2D Seismic data downloaded and processed successfully.")
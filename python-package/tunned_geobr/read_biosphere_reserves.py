import geopandas as gpd
import tempfile
import os
import gdown
from zipfile import ZipFile

def read_biosphere_reserves(simplified=False):
    """Download Brazilian Biosphere Reserves data.
    
    This function downloads and processes the Brazilian Biosphere Reserves data
    from a Google Drive repository. The data includes UNESCO Biosphere Reserves
    in Brazil, which are protected areas with high biodiversity value.
    Original source: MMA - Ministério do Meio Ambiente
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with Brazilian biosphere reserves data
        
    Example
    -------
    >>> from tunned_geobr import read_biosphere_reserves
    
    # Read biosphere reserves data
    >>> reserves = read_biosphere_reserves()
    """
    
    # Google Drive folder URL
    folder_url = "https://drive.google.com/drive/folders/19ygCKsQrI1gfRMe1jUbHZGQibbN_oLAC"
    
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the file from Google Drive
            output_zip = os.path.join(temp_dir, "biosphere_reserves.zip")
            
            # Use gdown to download the folder contents
            gdown.download_folder(folder_url, output=temp_dir, quiet=False)
            
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
                    'nome',        # Reserve name
                    'categoria',   # Category
                    'area_km2',    # Area in square kilometers
                    'bioma',       # Biome
                    'uf',          # State
                    'ano_criacao', # Creation year
                    'legislacao',  # Legislation
                    'orgao_gestor' # Managing agency
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading biosphere reserves data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_biosphere_reserves()

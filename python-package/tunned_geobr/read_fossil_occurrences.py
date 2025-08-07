import geopandas as gpd
import tempfile
import os
import requests
import fiona
from zipfile import ZipFile
from io import BytesIO

def read_fossil_occurrences(simplified=False):
    """Download Fossil Occurrences data from SGB.
    
    This function downloads and processes data about fossil occurrences in Brazil 
    from SGB (Serviço Geológico do Brasil). The data comes from a File Geodatabase (.gdb)
    and includes information about fossil sites across the country.
    Original source: SGB - Serviço Geológico do Brasil
    
    Parameters
    ----------
    simplified : boolean, by default False
        If True, returns a simplified version of the dataset with fewer columns
        
    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with fossil occurrences data
        
    Example
    -------
    >>> from tunned_geobr import read_fossil_occurrences
    
    # Read fossil occurrences data
    >>> fossils = read_fossil_occurrences()
    """
    
    url = "https://geoportal.sgb.gov.br/downloads/paleo.gdb.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from SGB")
            
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the .gdb.zip file
            gdb_zip = os.path.join(temp_dir, "paleo.gdb.zip")
            with open(gdb_zip, 'wb') as f:
                f.write(response.content)
            
            # Create the .gdb directory
            gdb_path = os.path.join(temp_dir, "paleo.gdb")
            os.makedirs(gdb_path, exist_ok=True)
            
            # Extract the .gdb.zip file directly into the .gdb directory
            with ZipFile(gdb_zip) as zip_ref:
                zip_ref.extractall(gdb_path)
            
            # List all layers in the GDB
            layers = fiona.listlayers(gdb_path)
            if not layers:
                raise Exception("No layers found in the GDB")
                
            # Read the first layer (assuming it's the fossil occurrences)
            gdf = gpd.read_file(gdb_path, layer=layers[0])
            gdf = gdf.to_crs(4674)  # Convert to SIRGAS 2000
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'LOCALIDADE',              # Locality name
                    'DISTRITO',                # District
                    'UNIDADE_LITOESTRATIGRAFICA',  # Lithostratigraphic unit
                    'UNIDADE_CRONOESTRATIGRAFICA', # Chronostratigraphic unit
                    'LITOLOGIA',               # Lithology
                    'VESTIGIOS_ORGANICOS',     # Organic traces
                    'AMBIENTE_DEPOSICAO',      # Depositional environment
                    'TAXON',                   # Taxon
                    'SISTEMATICA',             # Systematics
                    'MATERIAL',                # Material
                    'REFERENCIA_BIBLIOGRAFICA' # Bibliographic reference
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading fossil occurrences data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_fossil_occurrences()

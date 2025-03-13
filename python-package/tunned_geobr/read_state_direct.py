import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_state_direct(code_state="all", simplified=False):
    """Download shapefiles of Brazilian states as geopandas objects.

    This function downloads and processes state data directly from IBGE (Brazilian Institute of Geography and Statistics).
    Data uses Geodetic reference system "SIRGAS2000" and CRS(4674).
    
    Parameters
    ----------
    code_state : str, optional
        The two-digit code of a state or a two-letter uppercase abbreviation
        (e.g. 33 or "RJ"). If code_state="all", all states will be loaded (Default).
    simplified : boolean, by default True
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with state boundaries

    Example
    -------
    >>> from tunned_geobr import read_state

    # Read all states
    >>> states = read_state()

    # Read specific state by code
    >>> state = read_state(code_state=33)

    # Read specific state by abbreviation
    >>> state = read_state(code_state="RJ")
    """
    
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/Brasil/BR_UF_2023.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download state data from IBGE")
            
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
            
            # Convert to SIRGAS 2000 (EPSG:4674) if not already
            if gdf.crs is None or gdf.crs.to_epsg() != 4674:
                gdf = gdf.to_crs(4674)
            
            # Filter by code_state if not "all"
            if code_state != "all":
                if isinstance(code_state, int) or code_state.isdigit():
                    # Filter by numeric code
                    code = str(code_state).zfill(2)
                    gdf = gdf[gdf['CD_UF'] == code]
                elif isinstance(code_state, str) and len(code_state) == 2:
                    # Filter by state abbreviation
                    gdf = gdf[gdf['SIGLA_UF'] == code_state.upper()]
                
                if len(gdf) == 0:
                    raise Exception(f"No data found for code_state={code_state}")
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'CD_UF',       # State code
                    'SIGLA_UF',    # State abbreviation
                    'NM_UF',       # State name
                    'AREA_KM2'     # Area in square kilometers
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading state data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_state()

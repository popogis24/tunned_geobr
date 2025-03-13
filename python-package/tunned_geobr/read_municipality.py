import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO

def read_municipality(code_muni="all", simplified=False):
    """Download shapefiles of Brazilian municipalities as geopandas objects.

    This function downloads and processes municipality data directly from IBGE (Brazilian Institute of Geography and Statistics).
    Data uses Geodetic reference system "SIRGAS2000" and CRS(4674).
    
    Parameters
    ----------
    code_muni : str, optional
        The 7-digit code of a municipality. If the two-digit code or a two-letter uppercase abbreviation of
        a state is passed, (e.g. 33 or "RJ") the function will load all municipalities of that state.
        If code_muni="all", all municipalities of the country will be loaded (Default).
    simplified : boolean, by default True
        If True, returns a simplified version of the dataset with fewer columns

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with municipality boundaries

    Example
    -------
    >>> from tunned_geobr import read_municipality

    # Read all municipalities
    >>> municipalities = read_municipality()

    # Read all municipalities in a state by code
    >>> state_municipalities = read_municipality(code_muni=33)

    # Read all municipalities in a state by abbreviation
    >>> state_municipalities = read_municipality(code_muni="RJ")
    
    # Read specific municipality by code
    >>> municipality = read_municipality(code_muni=3304557)
    """
    
    url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/Brasil/BR_Municipios_2023.zip"
    
    try:
        # Download the zip file
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download municipality data from IBGE")
            
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
            
            # Filter by code_muni if not "all"
            if code_muni != "all":
                if isinstance(code_muni, int) or code_muni.isdigit():
                    if len(str(code_muni)) == 7:
                        # Filter by municipality code
                        gdf = gdf[gdf['CD_MUN'] == str(code_muni)]
                    elif len(str(code_muni)) == 2:
                        # Filter by state code
                        gdf = gdf[gdf['CD_MUN'].str.startswith(str(code_muni).zfill(2))]
                elif isinstance(code_muni, str) and len(code_muni) == 2:
                    # Filter by state abbreviation - need to get state code first
                    state_url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2023/Brasil/BR_UF_2023.zip"
                    state_response = requests.get(state_url)
                    
                    if state_response.status_code == 200:
                        with tempfile.TemporaryDirectory() as state_temp_dir:
                            with ZipFile(BytesIO(state_response.content)) as zip_ref:
                                zip_ref.extractall(state_temp_dir)
                            
                            state_shp_files = []
                            for root, dirs, files in os.walk(state_temp_dir):
                                state_shp_files.extend([os.path.join(root, f) for f in files if f.endswith('.shp')])
                            
                            if state_shp_files:
                                state_gdf = gpd.read_file(state_shp_files[0])
                                state_code = state_gdf[state_gdf['SIGLA_UF'] == code_muni.upper()]['CD_UF'].values
                                
                                if len(state_code) > 0:
                                    gdf = gdf[gdf['CD_MUN'].str.startswith(state_code[0])]
                
                if len(gdf) == 0:
                    raise Exception(f"No data found for code_muni={code_muni}")
            
            if simplified:
                # Keep only the most relevant columns
                columns_to_keep = [
                    'geometry',
                    'CD_MUN',      # Municipality code
                    'NM_MUN',      # Municipality name
                    'SIGLA_UF',    # State abbreviation
                    'AREA_KM2'     # Area in square kilometers
                ]
                
                # Filter columns that actually exist in the dataset
                existing_columns = ['geometry'] + [col for col in columns_to_keep[1:] if col in gdf.columns]
                gdf = gdf[existing_columns]
    
    except Exception as e:
        raise Exception(f"Error downloading municipality data: {str(e)}")
        
    return gdf

if __name__ == '__main__':
    read_municipality()

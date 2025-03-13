import geopandas as gpd
import requests
import shutil
import zipfile
import tempfile
import warnings
import os
from shapely.geometry.point import Point


def read_gas_transport_pipelines(simplified=False, verbose=False):
    """Download data of gas transport pipelines in Brazil.

    This function downloads and returns data of gas transport pipelines (gasodutos de transporte)
    in Brazil as a GeoPandas GeoDataFrame. The data comes from EPE (Energy Research Company).

    Parameters
    ----------
    simplified : bool, optional
        If True, returns a simplified version of the dataset with only the most
        important columns. If False, returns the complete dataset. Default is False.
    verbose : bool, optional
        If True, displays detailed messages about the download and processing
        steps. Default is False.

    Returns
    -------
    gpd.GeoDataFrame
        A GeoDataFrame containing data on gas transport pipelines in Brazil.

    Raises
    ------
    Exception
        If the download or processing of the data fails.

    Example
    -------
    >>> from tunned_geobr import read_gas_transport_pipelines
    >>> 
    >>> # Read the data
    >>> gas_pipelines = read_gas_transport_pipelines()
    >>> 
    >>> # Plot the data
    >>> gas_pipelines.plot()
    """
    
    if verbose:
        print("Downloading data of gas transport pipelines in Brazil")
    
    # Define the URL for the API request
    url = "https://gisepeprd2.epe.gov.br/arcgis/rest/services/Download_Dados_Webmap_EPE/GPServer/Extract%20Data%20Task/execute?f=json&env%3AoutSR=102100&Layers_to_Clip=%5B%22Gasodutos%20de%20transporte%22%5D&Area_of_Interest=%7B%22geometryType%22%3A%22esriGeometryPolygon%22%2C%22features%22%3A%5B%7B%22geometry%22%3A%7B%22rings%22%3A%5B%5B%5B-8655251.47456396%2C-4787514.465591563%5D%2C%5B-8655251.47456396%2C1229608.401015912%5D%2C%5B-3508899.2341809804%2C1229608.401015912%5D%2C%5B-3508899.2341809804%2C-4787514.465591563%5D%2C%5B-8655251.47456396%2C-4787514.465591563%5D%5D%5D%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D%7D%5D%2C%22sr%22%3A%7B%22wkid%22%3A102100%7D%7D&Feature_Format=Shapefile%20-%20SHP%20-%20.shp&Raster_Format=Tagged%20Image%20File%20Format%20-%20TIFF%20-%20.tif"
    
    try:
        # Make the API request
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the URL for the zip file
        if 'results' in data and len(data['results']) > 0 and 'value' in data['results'][0]:
            download_url = data['results'][0]['value']['url']
        else:
            raise Exception("Failed to extract download URL from API response")
        
        # Create a temporary directory to store the downloaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download the zip file
            zip_path = os.path.join(temp_dir, "gas_transport_pipelines.zip")
            if verbose:
                print("Downloading zip file")
            
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
            
            # Extract the zip file
            if verbose:
                print("Extracting files")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            zip_dir = os.path.join(temp_dir,'zipfolder')
            # Find the shapefile in the extracted files
            shp_files = [f for f in os.listdir(zip_dir) if f.endswith('.shp')]
            
            if not shp_files:
                raise Exception("No shapefile found in the downloaded zip file")
            
            # Read the shapefile
            if verbose:
                print("Reading shapefile")
            
            shp_path = os.path.join(zip_dir, shp_files[0])
            gdf = gpd.read_file(shp_path)
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            if verbose:
                print("Converting to SIRGAS 2000 (EPSG:4674)")
            
            gdf = gdf.to_crs(epsg=4674)
            
            # Simplify the dataset if requested
            if simplified:
                if verbose:
                    print("Simplifying the dataset")
                
                # Select only the most important columns
                # Adjust these columns based on the actual data structure
                cols_to_keep = ['NOME', 'EMPRESA', 'EXTENSAO', 'DIAMETRO', 'CAPACIDADE', 'UF', 'geometry']
                cols_available = [col for col in cols_to_keep if col in gdf.columns]
                
                if not cols_available:
                    warnings.warn("None of the specified columns for simplification are available. Returning the full dataset.")
                else:
                    gdf = gdf[cols_available]
            
            if verbose:
                print("Finished processing gas transport pipelines data")
            
            return gdf
    
    except Exception as e:
        raise Exception(f"Failed to download or process gas transport pipelines data: {str(e)}")

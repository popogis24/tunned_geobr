import geopandas as gpd
import requests
import zipfile
import tempfile
import os
import warnings
import shutil


def read_og_ipa_direct_evidence(simplified=True, verbose=False):
    """Download data for Oil and Gas IPA Direct Evidence of Hydrocarbons in Brazil.

    This function downloads, processes, and returns data for Oil and Gas IPA Direct Evidence of Hydrocarbons
    in Brazil as a geopandas GeoDataFrame.

    Parameters
    ----------
    simplified : bool, optional
        If True, returns a simplified version of the dataset with only essential columns.
        If False, returns the complete dataset with all columns.
        Default is True.
    verbose : bool, optional
        If True, prints detailed information about the data download and processing.
        Default is False.

    Returns
    -------
    geopandas.GeoDataFrame
        A GeoDataFrame containing Oil and Gas IPA Direct Evidence of Hydrocarbons data.

    Examples
    --------
    >>> # Download Oil and Gas IPA Direct Evidence of Hydrocarbons data
    >>> df = read_og_ipa_direct_evidence()
    >>> df.head()
    """

    url = "https://gisepeprd2.epe.gov.br/arcgis/rest/services/Download_Dados_Webmap_EPE/GPServer/Extract%20Data%20Task/execute?f=json&env%3AoutSR=102100&Layers_to_Clip=%5B%22IPA%20Evid%C3%AAncia%20Direta%20de%20Hidrocarbonetos%22%5D&Area_of_Interest=%7B%22geometryType%22%3A%22esriGeometryPolygon%22%2C%22features%22%3A%5B%7B%22geometry%22%3A%7B%22rings%22%3A%5B%5B%5B-9237395.881983705%2C-4650539.310904562%5D%2C%5B-9237395.881983705%2C1219824.4613954136%5D%2C%5B-2349502.3891517334%2C1219824.4613954136%5D%2C%5B-2349502.3891517334%2C-4650539.310904562%5D%2C%5B-9237395.881983705%2C-4650539.310904562%5D%5D%5D%2C%22spatialReference%22%3A%7B%22wkid%22%3A102100%7D%7D%7D%5D%2C%22sr%22%3A%7B%22wkid%22%3A102100%7D%7D&Feature_Format=Shapefile%20-%20SHP%20-%20.shp&Raster_Format=Tagged%20Image%20File%20Format%20-%20TIFF%20-%20.tif"

    if verbose:
        print("Downloading data...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()

        if "value" not in response_json or not response_json["value"]:
            raise ValueError("No data found in the response")

        download_url = response_json["value"]["itemUrl"]
        
        if verbose:
            print(f"Download URL: {download_url}")
            print("Downloading zip file...")

        zip_response = requests.get(download_url)
        zip_response.raise_for_status()

        # Create a temporary directory to extract the files
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "data.zip")
            
            # Save the zip file
            with open(zip_path, "wb") as f:
                f.write(zip_response.content)
            
            if verbose:
                print(f"Zip file saved to {zip_path}")
                print("Extracting files...")
            
            # Extract the zip file
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Find the shapefile
            shp_files = [f for f in os.listdir(temp_dir) if f.endswith(".shp")]
            
            if not shp_files:
                raise FileNotFoundError("No shapefile found in the downloaded zip file")
            
            shp_path = os.path.join(temp_dir, shp_files[0])
            
            if verbose:
                print(f"Reading shapefile from {shp_path}")
            
            # Read the shapefile
            gdf = gpd.read_file(shp_path)
            
            # Convert to SIRGAS 2000 (EPSG:4674)
            gdf = gdf.to_crs(epsg=4674)
            
            if simplified:
                # Select only essential columns
                if verbose:
                    print("Simplifying the dataset...")
                
                # Identify the essential columns
                essential_cols = ["geometry"]
                
                # Add any other essential columns that exist in the dataset
                for col in ["CLASSE", "NOME", "DESCRICAO", "AREA_KM2"]:
                    if col in gdf.columns:
                        essential_cols.append(col)
                
                # Select only the essential columns
                gdf = gdf[essential_cols]
            
            return gdf
    
    except requests.exceptions.RequestException as e:
        warnings.warn(f"Error downloading data: {e}")
        return None
    except (ValueError, FileNotFoundError, zipfile.BadZipFile) as e:
        warnings.warn(f"Error processing data: {e}")
        return None
    except Exception as e:
        warnings.warn(f"Unexpected error: {e}")
        return None


from geobr.utils import select_metadata, download_gpkg


def read_municipal_seat(year=2010, tp='normal', verbose=False):
    """ Download official data of municipal seats (sede dos municipios) in Brazil as an sf object.
    
     This function reads the official data on the municipal seats (sede dos municipios) of Brazil.
 The data brings the spatial coordinates (lat lon) of of municipal seats for various years
 between 1872 and 2010. Orignal data were generated by Brazilian Institute of Geography
 and Statistics (IBGE).

    Parameters
    ----------
    year : int, optional
        Year of the data, by default 2010
    tp : str, optional
        Data 'type', indicating whether the function returns the 'original' dataset 
        with high resolution or a dataset with 'simplified' borders (Default)
    verbose : bool, optional
        by default False
    
    Returns
    -------
    gpd.GeoDataFrame
        Metadata and geopackage of selected states
    
    Raises
    ------
    Exception
        If parameters are not found or not well defined

    Example
    -------
    >>> from geobr import read_municipal_seat

    # Read specific state at a given year
    >>> df = read_municipal_seat(year=2010)
    """

    metadata = select_metadata('municipal_seat', year=year, data_type=tp)

    gdf = download_gpkg(metadata)

    return gdf
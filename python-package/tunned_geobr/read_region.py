from geobr import read_region as _read_region


def read_region(year=2010, simplified=False, verbose=False):
    """ Download shape file of Brazil Regions as sf objects.
    
    Data at scale 1:250,000, using Geodetic reference system "SIRGAS2000" and CRS(4674)

    Parameters
    ----------
    year : int, optional
        Year of the data, by default 2010
    simplified: boolean, by default True
        Data 'type', indicating whether the function returns the 'original' dataset 
        with high resolution or a dataset with 'simplified' borders (Default)
    verbose : bool, optional
        by default False
    
    Returns
    -------
    gpd.GeoDataFrame
        Metadata and geopackage of selected states
    
    Example
    -------
    >>> from tunned_geobr import read_region

    # Read specific state at a given year
    >>> df = read_region(year=2010)
    """
    return _read_region(year=year, simplified=simplified, verbose=verbose)

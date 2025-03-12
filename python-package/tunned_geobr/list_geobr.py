import pandas as pd
from tabulate import tabulate

def list_geobr():
    """Lists all available datasets in the tunned_geobr package.
    
    This function displays a comprehensive table of all geographic datasets
    available in the tunned_geobr package, including information about the
    geographies, years, and sources.
    
    Returns
    -------
    pandas.DataFrame
        A DataFrame containing information about all available datasets
    
    Example
    -------
    >>> from tunned_geobr import list_geobr
    >>> datasets = list_geobr()
    """
    
    # Create a comprehensive list of all datasets
    datasets = [
        # Original geobr datasets
        {"Function": "read_country", "Geography": "Country", "Years": "All", "Source": "IBGE"},
        {"Function": "read_region", "Geography": "Region", "Years": "All", "Source": "IBGE"},
        {"Function": "read_state", "Geography": "State", "Years": "All", "Source": "IBGE"},
        {"Function": "read_state_direct", "Geography": "State", "Years": "All", "Source": "IBGE"},
        {"Function": "read_meso_region", "Geography": "Meso region", "Years": "1991, 2000, 2010, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020", "Source": "IBGE"},
        {"Function": "read_micro_region", "Geography": "Micro region", "Years": "1991, 2000, 2010, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020", "Source": "IBGE"},
        {"Function": "read_immediate_region", "Geography": "Immediate region", "Years": "2017, 2019, 2020", "Source": "IBGE"},
        {"Function": "read_intermediate_region", "Geography": "Intermediate region", "Years": "2017, 2019, 2020", "Source": "IBGE"},
        {"Function": "read_municipality", "Geography": "Municipality", "Years": "All", "Source": "IBGE"},
        {"Function": "read_municipality_direct", "Geography": "Municipality", "Years": "All", "Source": "IBGE"},
        {"Function": "read_weighting_area", "Geography": "Census weighting area", "Years": "2010", "Source": "IBGE"},
        {"Function": "read_census_tract", "Geography": "Census tract", "Years": "2000, 2010", "Source": "IBGE"},
        {"Function": "read_census_tract_2022", "Geography": "Census tract 2022", "Years": "2022", "Source": "IBGE"},
        {"Function": "read_statistical_grid", "Geography": "Statistical grid", "Years": "2010", "Source": "IBGE"},
        {"Function": "read_comparable_areas", "Geography": "Comparable areas", "Years": "1872, 1900, 1911, 1920, 1933, 1940, 1950, 1960, 1970, 1980, 1991, 2000, 2010", "Source": "IBGE"},
        {"Function": "read_health_region", "Geography": "Health region", "Years": "1991, 1994, 1997, 2001, 2005, 2013", "Source": "DataSUS"},
        {"Function": "read_metro_area", "Geography": "Metropolitan area", "Years": "All", "Source": "IBGE"},
        {"Function": "read_urban_area", "Geography": "Urban area", "Years": "2005, 2015", "Source": "IBGE"},
        {"Function": "read_urban_concentrations", "Geography": "Urban concentrations", "Years": "All", "Source": "IBGE"},
        {"Function": "read_amazon", "Geography": "Amazon", "Years": "All", "Source": "IBGE, MMA, and others"},
        {"Function": "read_biomes", "Geography": "Biomes", "Years": "2004, 2019", "Source": "IBGE"},
        {"Function": "read_conservation_units", "Geography": "Conservation units", "Years": "All", "Source": "MMA"},
        {"Function": "read_disaster_risk_area", "Geography": "Disaster risk areas", "Years": "2010", "Source": "CEMADEN and IBGE"},
        {"Function": "read_indigenous_land", "Geography": "Indigenous lands", "Years": "All", "Source": "FUNAI"},
        {"Function": "read_semiarid", "Geography": "Semi-arid region", "Years": "All", "Source": "IBGE and others"},
        {"Function": "read_health_facilities", "Geography": "Health facilities", "Years": "All", "Source": "DataSUS"},
        {"Function": "read_neighborhood", "Geography": "Neighborhood", "Years": "2010", "Source": "IBGE"},
        {"Function": "read_neighborhoods_2022", "Geography": "Neighborhoods 2022", "Years": "2022", "Source": "IBGE"},
        {"Function": "read_schools", "Geography": "Schools", "Years": "All", "Source": "INEP"},
        {"Function": "read_ports", "Geography": "Ports", "Years": "All", "Source": "Ministério da Infraestrutura"},
        {"Function": "read_municipal_seat", "Geography": "Municipal seats", "Years": "All", "Source": "IBGE"},
        {"Function": "read_pop_arrangements", "Geography": "Population arrangements", "Years": "2015", "Source": "IBGE"},
        {"Function": "read_rppn", "Geography": "Private Natural Heritage Reserves", "Years": "All", "Source": "ICMBio"},
        {"Function": "read_settlements", "Geography": "Rural settlements", "Years": "All", "Source": "INCRA"},
        
        # Additional datasets in tunned_geobr
        {"Function": "read_mining_processes", "Geography": "Mining processes", "Years": "All", "Source": "ANM"},
        {"Function": "read_ebas", "Geography": "Endemic Bird Areas", "Years": "All", "Source": "Global Forest Watch"},
        {"Function": "read_vegetation", "Geography": "Brazilian Vegetation", "Years": "All", "Source": "IBGE"},
        {"Function": "read_transmission_lines_ons", "Geography": "Transmission Lines", "Years": "All", "Source": "ONS"},
        {"Function": "read_water_bodies_ana", "Geography": "Water Bodies", "Years": "All", "Source": "ANA"},
        {"Function": "read_pan_strategic_areas", "Geography": "PAN Strategic Areas", "Years": "All", "Source": "ICMBio"},
        {"Function": "read_geographic_regions", "Geography": "Geographic Regions", "Years": "All", "Source": "IBGE"},
        {"Function": "read_biosphere_reserves", "Geography": "Biosphere Reserves", "Years": "All", "Source": "MMA"},
        {"Function": "read_baze_sites", "Geography": "BAZE Sites", "Years": "2018", "Source": "MMA"},
        
        # Environmental and conservation datasets
        {"Function": "read_amazon_ibas", "Geography": "Amazon IBAs", "Years": "All", "Source": "SAVE Brasil"},
        {"Function": "read_atlantic_forest_ibas", "Geography": "Atlantic Forest IBAs", "Years": "All", "Source": "SAVE Brasil"},
        {"Function": "read_atlantic_forest_law_limits", "Geography": "Atlantic Forest Law Limits", "Years": "All", "Source": "MMA/IBGE"},
        {"Function": "read_apcb_amazon", "Geography": "APCB Amazon", "Years": "All", "Source": "MMA"},
        {"Function": "read_apcb_caatinga", "Geography": "APCB Caatinga", "Years": "All", "Source": "MMA"},
        {"Function": "read_apcb_cerrado_pantanal", "Geography": "APCB Cerrado/Pantanal", "Years": "All", "Source": "MMA"},
        {"Function": "read_apcb_mata_atlantica", "Geography": "APCB Atlantic Forest", "Years": "All", "Source": "MMA"},
        {"Function": "read_apcb_pampa", "Geography": "APCB Pampa", "Years": "All", "Source": "MMA"},
        {"Function": "read_apcb_zcm", "Geography": "APCB Coastal/Marine", "Years": "All", "Source": "MMA"},
        
        # Geological and natural features datasets
        {"Function": "read_natural_caves", "Geography": "Natural Caves", "Years": "All", "Source": "ICMBio"},
        {"Function": "read_cave_potential", "Geography": "Cave Potential", "Years": "All", "Source": "ICMBio"},
        {"Function": "read_fossil_occurrences", "Geography": "Fossil Occurrences", "Years": "All", "Source": "SGB"},
        {"Function": "read_archaeological_sites", "Geography": "Archaeological Sites", "Years": "All", "Source": "IPHAN"},
        {"Function": "read_geology", "Geography": "Geology", "Years": "All", "Source": "CPRM"},
        {"Function": "read_geomorphology", "Geography": "Geomorphology", "Years": "All", "Source": "IBGE"},
        {"Function": "read_pedology", "Geography": "Pedology", "Years": "All", "Source": "IBGE"},
        {"Function": "read_climate_aggressiveness", "Geography": "Climate Aggressiveness", "Years": "All", "Source": "IBGE"},
        
        # Transportation and infrastructure datasets
        {"Function": "read_public_aerodromes", "Geography": "Public Aerodromes", "Years": "All", "Source": "MapBiomas"},
        {"Function": "read_private_aerodromes", "Geography": "Private Aerodromes", "Years": "All", "Source": "MapBiomas"},
        {"Function": "read_state_highways", "Geography": "State Highways", "Years": "All", "Source": "MapBiomas"},
        {"Function": "read_federal_highways", "Geography": "Federal Highways", "Years": "All", "Source": "MapBiomas"},
        {"Function": "read_railways", "Geography": "Railways", "Years": "All", "Source": "MapBiomas"},
        {"Function": "read_waterways", "Geography": "Waterways", "Years": "All", "Source": "SNIRH"},
        {"Function": "read_heliports", "Geography": "Heliports", "Years": "All", "Source": "MapBiomas"},
        
        # Land tenure and property datasets
        {"Function": "read_snci_properties", "Geography": "SNCI Properties", "Years": "All", "Source": "INCRA"},
        {"Function": "read_sigef_properties", "Geography": "SIGEF Properties", "Years": "All", "Source": "INCRA"},
        {"Function": "read_quilombola_areas", "Geography": "Quilombola Areas", "Years": "All", "Source": "INCRA"}
    ]
    
    # Create DataFrame
    df = pd.DataFrame(datasets)
    
    # Display the table
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    
    # Return the DataFrame for further use
    return df

if __name__ == "__main__":
    list_geobr()

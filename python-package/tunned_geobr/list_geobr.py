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
        {"Function": "read_quilombola_areas", "Geography": "Quilombola Areas", "Years": "All", "Source": "INCRA"},
        
        # Energy infrastructure datasets - Solar
        {"Function": "read_existent_solar", "Geography": "Existing Solar Power Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_solar", "Geography": "Planned Solar Power Plants", "Years": "All", "Source": "EPE"},
        
        # Energy infrastructure datasets - Wind
        {"Function": "read_existent_eolic", "Geography": "Existing Wind Power Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_eolic", "Geography": "Planned Wind Power Plants", "Years": "All", "Source": "EPE"},
        
        # Energy infrastructure datasets - Hydroelectric
        {"Function": "read_existent_uhe", "Geography": "Existing Large Hydroelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_existent_pch", "Geography": "Existing Small Hydroelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_existent_cgh", "Geography": "Existing Mini Hydroelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_uhe", "Geography": "Planned Large Hydroelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_pch", "Geography": "Planned Small Hydroelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_cgh", "Geography": "Planned Mini Hydroelectric Plants", "Years": "All", "Source": "EPE"},
        
        # Energy infrastructure datasets - Thermoelectric
        {"Function": "read_existent_biomass_ute", "Geography": "Existing Biomass Thermoelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_existent_fossile_ute", "Geography": "Existing Fossil Thermoelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_existent_nuclear_ute", "Geography": "Existing Nuclear Thermoelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_biomass_ute", "Geography": "Planned Biomass Thermoelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_fossile_ute", "Geography": "Planned Fossil Thermoelectric Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_nuclear_ute", "Geography": "Planned Nuclear Thermoelectric Plants", "Years": "All", "Source": "EPE"},
        
        # Energy infrastructure datasets - Transmission
        {"Function": "read_existent_substations", "Geography": "Existing Electrical Substations", "Years": "All", "Source": "EPE"},
        {"Function": "read_existent_transmission_lines", "Geography": "Existing Transmission Lines", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_substations", "Geography": "Planned Electrical Substations", "Years": "All", "Source": "EPE"},
        {"Function": "read_planned_transmission_lines", "Geography": "Planned Transmission Lines", "Years": "All", "Source": "EPE"},
        {"Function": "read_subsystem_interconnected", "Geography": "National Interconnected System Subsystems", "Years": "All", "Source": "EPE"},
        {"Function": "read_isolated_systems", "Geography": "Isolated Electrical Systems", "Years": "All", "Source": "EPE"},
        
        # Energy infrastructure datasets - Biofuel Plants
        {"Function": "read_etanol_plants", "Geography": "Ethanol Production Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_biodiesel_plants", "Geography": "Biodiesel Production Plants", "Years": "All", "Source": "EPE"},
        {"Function": "read_biomethane_plants", "Geography": "Biomethane Production Plants", "Years": "All", "Source": "EPE"},
        
        # Energy infrastructure datasets - Oil and Gas Infrastructure
        {"Function": "read_fuel_bases", "Geography": "Fuel Bases", "Years": "All", "Source": "EPE"},
        {"Function": "read_glp_bases", "Geography": "GLP (LPG) Bases", "Years": "All", "Source": "EPE"},
        {"Function": "read_processing_facilities", "Geography": "Oil and Gas Processing Facilities", "Years": "All", "Source": "EPE"},
        {"Function": "read_oil_and_derivatives_terminal", "Geography": "Oil and Derivatives Terminals", "Years": "All", "Source": "EPE"},
        {"Function": "read_pio_terminals", "Geography": "PIO Terminals", "Years": "All", "Source": "EPE"},
        {"Function": "read_pio_ducts", "Geography": "PIO Ducts", "Years": "All", "Source": "EPE"},
        {"Function": "read_gnl_terminals", "Geography": "GNL (LNG) Terminals", "Years": "All", "Source": "EPE"},
        {"Function": "read_natural_gas_processing_hub", "Geography": "Natural Gas Processing Hubs", "Years": "All", "Source": "EPE"},
        {"Function": "read_compression_stations", "Geography": "Natural Gas Compression Stations", "Years": "All", "Source": "EPE"},
        {"Function": "read_natural_gas_delivery_points", "Geography": "Natural Gas Delivery Points", "Years": "All", "Source": "EPE"},
        {"Function": "read_gas_transport_pipelines", "Geography": "Gas Transport Pipelines", "Years": "All", "Source": "EPE"},
        {"Function": "read_gas_distribution_pipelines", "Geography": "Gas Distribution Pipelines", "Years": "All", "Source": "EPE"},
        {"Function": "read_areas_under_contract", "Geography": "Oil and Gas Areas Under Contract", "Years": "All", "Source": "EPE"},
        {"Function": "read_federal_union_areas", "Geography": "Federal Union Areas for Oil and Gas", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_effective_geographic_basin", "Geography": "Oil and Gas Effective Geographic Basins", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_probabilistic_effective_basin", "Geography": "Oil and Gas Probabilistic Effective Basins", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_predominant_fluid_type", "Geography": "Oil and Gas Predominant Fluid Type Areas", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_unconventional_resources", "Geography": "Oil and Gas Unconventional Resources", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_total_ipa", "Geography": "Oil and Gas Total IPA", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_ipa_exploratory_intensity", "Geography": "Oil and Gas IPA Exploratory Intensity", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_ipa_exploratory_activity", "Geography": "Oil and Gas IPA Exploratory Activity", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_ipa_prospectiveness", "Geography": "Oil and Gas IPA Prospectiveness", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_ipa_direct_evidence", "Geography": "Oil and Gas IPA Direct Evidence of Hydrocarbons", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_ipa_need_for_knowledge", "Geography": "Oil and Gas IPA Need for Knowledge", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_ipa_supply_infrastructure", "Geography": "Oil and Gas IPA Supply Infrastructure", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_legal_pre_salt_polygon", "Geography": "Oil and Gas Legal Pre-Salt Polygon", "Years": "All", "Source": "EPE"},
        {"Function": "read_exploration_production_environment", "Geography": "Exploration and Production Environment", "Years": "All", "Source": "EPE"},
        {"Function": "read_sedimentary_basins", "Geography": "Sedimentary Basins", "Years": "All", "Source": "EPE"},
        {"Function": "read_og_basement", "Geography": "Oil and Gas Basement", "Years": "All", "Source": "EPE"},
        {"Function": "read_hydroelectric_feasibility_studies", "Geography": "Hydroelectric Feasibility Studies", "Years": "All", "Source": "EPE"},
        {"Function": "read_hydroelectric_inventory_aai_studies", "Geography": "Hydroelectric Inventory and AAI Studies", "Years": "All", "Source": "EPE"},
        {"Function": "read_ama_anemometric_towers", "Geography": "AMA Anemometric Towers", "Years": "All", "Source": "EPE"}
    ]
    
    # Create DataFrame
    df = pd.DataFrame(datasets)
    
    # Display the table
    print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
    
    # Return the DataFrame for further use
    return df

if __name__ == "__main__":
    list_geobr()

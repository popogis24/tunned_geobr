import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO


def read_economically_navigable_inland_waterways(simplified: bool = False) -> gpd.GeoDataFrame:
    """Download ANTAQ economically navigable inland waterways.

    This function downloads and processes the ANTAQ dataset of economically
    navigable inland waterways. The source file is distributed as a zipped
    shapefile.

    Parameters
    ----------
    simplified : bool, optional
        If True, returns a simplified version of the dataset with a curated
        subset of columns, by default False.

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with ANTAQ inland waterways.

    Example
    -------
    >>> from tunned_geobr import read_antaq_economic_waterways
    >>> waterways = read_antaq_economic_waterways()
    """

    url = (
        "https://www.gov.br/antaq/pt-br/central-de-conteudos/"
        "SHP_VEN2022completo.zip"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                "Failed to download economically navigable waterways from ANTAQ"
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            with ZipFile(BytesIO(response.content)) as zip_ref:
                zip_ref.extractall(temp_dir)

            shapefiles = []
            for root, _, files in os.walk(temp_dir):
                shapefiles.extend(
                    [
                        os.path.join(root, f)
                        for f in files
                        if f.lower().endswith(".shp")
                    ]
                )

            if not shapefiles:
                raise Exception("No shapefile found in the downloaded ANTAQ data")

            preferred = next(
                (
                    path
                    for path in shapefiles
                    if any(
                        keyword in os.path.basename(path).lower()
                        for keyword in ("ven", "naveg", "hidro")
                    )
                ),
                shapefiles[0],
            )

            gdf = gpd.read_file(preferred)
            gdf = gdf.to_crs(4674)

            if simplified:
                desired_columns = [
                    "geometry",
                    "fase",
                    "trecho",
                    "hidrovia",
                    "uf",
                    "situacao",
                    "tipo",
                    "classe",
                    "orgao",
                    "extensao",
                ]

                normalized_map = {
                    col.lower(): col for col in gdf.columns if col.lower() != "geometry"
                }

                columns_to_keep = ["geometry"]
                for col in desired_columns[1:]:
                    matched = normalized_map.get(col)
                    if matched:
                        columns_to_keep.append(matched)

                gdf = gdf[[c for c in columns_to_keep if c in gdf.columns]]

    except Exception as exc:
        raise Exception(
            f"Error downloading ANTAQ economically navigable waterways: {str(exc)}"
        ) from exc

    return gdf

if __name__ == '__main__':
    read_economically_navigable_inland_waterways(simplified=False)
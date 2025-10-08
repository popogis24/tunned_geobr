import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO


def read_granted_crossing_lines(simplified: bool = False) -> gpd.GeoDataFrame:
    """Download Brazilian authorized crossing lines from ANTAQ.

    This function downloads and processes the ANTAQ (Agência Nacional de
    Transportes Aquaviários) dataset of authorized water crossing lines.
    The source is provided as a zipped shapefile.

    Parameters
    ----------
    simplified : bool, optional
        If True, returns a simplified version of the dataset with a curated
        subset of columns, by default False.

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe containing ANTAQ authorized crossing lines.

    Example
    -------
    >>> from tunned_geobr import read_antaq_crossing_lines
    >>> crossing_lines = read_antaq_crossing_lines()
    """

    url = (
        "https://www.gov.br/antaq/pt-br/central-de-conteudos/"
        "Linhasdetravessias06052025.zip"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download crossing lines data from ANTAQ")

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
                    if any(keyword in os.path.basename(path).lower() for keyword in ("trav", "linha"))
                ),
                shapefiles[0],
            )

            gdf = gpd.read_file(preferred)
            gdf = gdf.to_crs(4674)

            if simplified:
                desired_columns = [
                    "geometry",
                    "linha",
                    "travessia",
                    "empresa",
                    "municipio",
                    "uf",
                    "situacao",
                    "modalidade",
                    "orgao",
                    "cnpj",
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
            f"Error downloading ANTAQ crossing lines data: {str(exc)}"
        ) from exc

    return gdf

if __name__ == "__main__":
    # Example usage
    crossing_lines = read_granted_crossing_lines(simplified=False)
    print(crossing_lines.head())
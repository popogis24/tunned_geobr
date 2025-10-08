import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO


def read_granted_port_facilities(simplified: bool = False) -> gpd.GeoDataFrame:
    """Download Brazilian port facility data from ANTAQ.

    This function downloads and processes the official ANTAQ (Agência Nacional de
    Transportes Aquaviários) dataset of port facilities across Brazil. The source
    file is distributed as a zipped shapefile.

    Parameters
    ----------
    simplified : bool, optional
        If True, returns a simplified version of the dataset with a curated
        subset of columns, by default False.

    Returns
    -------
    gpd.GeoDataFrame
        Geodataframe with ANTAQ port facilities.

    Example
    -------
    >>> from tunned_geobr import read_antaq_ports
    >>> antaq_ports = read_antaq_ports()
    """

    url = (
        "https://www.gov.br/antaq/pt-br/central-de-conteudos/"
        "Instalaesporturias06052025.zip"
    )

    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download data from ANTAQ")

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
                (path for path in shapefiles if "Portos" in os.path.basename(path).lower()),
                shapefiles[0],
            )

            gdf = gpd.read_file(preferred)
            gdf = gdf.to_crs(4674)

            if simplified:
                desired_columns = [
                    "geometry",
                    "nome",
                    "municipio",
                    "uf",
                    "tipologia",
                    "tipo",
                    "segmento",
                    "situacao",
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

                # Always keep geometry even if no attributes matched
                gdf = gdf[[c for c in columns_to_keep if c in gdf.columns]]

    except Exception as exc:
        raise Exception(f"Error downloading ANTAQ ports data: {str(exc)}") from exc

    return gdf

if __name__ == "__main__":
    read_granted_port_facilities()
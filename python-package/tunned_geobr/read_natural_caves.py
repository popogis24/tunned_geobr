import geopandas as gpd
import tempfile
import os
import requests
from zipfile import ZipFile
from io import BytesIO
from time import sleep
import pandas as pd
import cloudscraper
from shapely.geometry import Point

def read_natural_caves(simplified=False):
    """
    Baixa e junta relatórios do CANIE por 'Número CANIE'.
    Se simplified=True, retorna apenas algumas colunas.
    """
    urls = {
        "BASE": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,2,3,4,5,6,7,8,9&download=true&type=xlsx",
        "CAVERNA IMPACTADA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,10&download=true&type=xlsx",
        "PROCESSO DE LICENCIAMENTO": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,11&download=true&type=xlsx",
        "UNIDADE ESPELEOLOGICA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,12&download=true&type=xlsx",
        "UNIDADE GEOMORFOLOGICA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,13&download=true&type=xlsx",
        "NOME DO PROPRIETARIO": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,14&download=true&type=xlsx",
        "AREA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,15&download=true&type=xlsx",
        "DESNIVEL": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,16&download=true&type=xlsx",
        "VOLUME": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,17&download=true&type=xlsx",
        "PROJECAO HORIZONTAL": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,18&download=true&type=xlsx",
        "DESENVOLVIMENTO LINEAR": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,19&download=true&type=xlsx",
        "ORGAO LICENCIADOR": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,20&download=true&type=xlsx",
        "LITOLOGIA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,21&download=true&type=xlsx",
        "REGIAO HIDROGRAFICA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,22&download=true&type=xlsx",
        "CADASTRADOR": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,23&download=true&type=xlsx",
        "GRAU DE RELEVANCIA": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,24&download=true&type=xlsx",
        "DATA DE CADASTRO": "https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2?items=1,25&download=true&type=xlsx"
    }

    download_links = []
    
    scraper = cloudscraper.create_scraper()    

    with tempfile.TemporaryDirectory() as tmpdir:
        dfs = []

        # Requisições normais
        for key, url in urls.items():
            try:
                response = scraper.get(url)
                response.raise_for_status()
                json_data = response.json()
                filename = json_data["data"]
                download_url = f"https://canie2.sisicmbio.icmbio.gov.br/api/v1/reports/dynamic-reports2/download-report?name={filename}"
                download_links.append(download_url)
            except Exception as e:
                print(f"[ERRO] Falha ao gerar {key}: {e}")

        # Download + leitura
        for i, download_url in enumerate(download_links):
            try:
                response = scraper.get(download_url)
                response.raise_for_status()
                local_path = os.path.join(tmpdir, f"file_{i}.xlsx")
                with open(local_path, "wb") as f:
                    f.write(response.content)

                df = pd.read_excel(local_path, header=8)  # Cabeçalho na linha 9
                dfs.append(df)

            except Exception as e:
                print(f"[ERRO] Falha ao baixar/ler {download_url}: {e}")

        # Merge sequencial usando "Número CANIE"
        merged_df = dfs[0]
        for df in dfs[1:]:
            merged_df = pd.merge(merged_df, df, on="Número CANIE", how="outer")

        if simplified:
            colunas = [col for col in merged_df.columns if any(x in col.lower() for x in ["canie", "nome", "caverna", "grau", "relevancia", "licenciamento"])]
            return merged_df[colunas]
        

        geometry = [Point(xy) for xy in zip(merged_df["Longitude"], merged_df["Latitude"])]
        gdf = gpd.GeoDataFrame(merged_df, geometry=geometry, crs="EPSG:4674")
        
        return gdf

if __name__ == "__main__":
    # Exemplo de uso
    caves_df = read_natural_caves(simplified=False)
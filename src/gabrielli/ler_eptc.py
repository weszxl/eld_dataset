import glob
import os
import shutil
import tempfile
import zipfile
import geopandas as gpd

""" --------- Código utilizado para transformar os shapefiles em CSV e GeoJson -----------
https://drive.procempa.com.br/s/LJp8MNCFmZKdPpD link que utilizei para extrair os dados zipados e após isso tranformar em csv e gson
-> dados extraidos
Bairros, BikePOA, Ciclovias implentadas, Corredores de faixas exclusivas, Eixos de logradouros, Paraciclos emplantados, paradas e rede cicloviaria.
"""

PASTA_ENTRADA = "eptc_zips"
PASTA_SAIDA = "dados_eptc"
ENC = None  

# projeção local de Porto Alegre 
CRS_POA = ("+proj=tmerc +lat_0=0 +lon_0=-51 +k=0.999995 "
           "+x_0=300000 +y_0=5000000 +ellps=WGS84 +units=m +no_defs")

os.makedirs(PASTA_SAIDA, exist_ok=True)


def ler(shp):
    """Lê o shapefile; se o .prj não for reconhecido, define a projeção à mão."""
    try:
        return gpd.read_file(shp, encoding=ENC), False
    except Exception as e:
        if "Invalid projection" not in str(e):
            raise
        base = os.path.splitext(shp)[0]
        nome = os.path.basename(base)
        tmp = tempfile.mkdtemp()
        for ext in (".shp", ".shx", ".dbf", ".cpg"):  # copia sem o .prj
            if os.path.exists(base + ext):
                shutil.copy(base + ext, os.path.join(tmp, nome + ext))
        g = gpd.read_file(os.path.join(tmp, nome + ".shp"), encoding=ENC)
        return g.set_crs(CRS_POA), True


# descompacta .zip que ainda estiverem compactados
for z in glob.glob(f"{PASTA_ENTRADA}/**/*.zip", recursive=True):
    destino = z[:-4]
    if not os.path.isdir(destino):
        with zipfile.ZipFile(z) as f:
            f.extractall(destino)
        print("descompactado:", os.path.basename(z))

arquivos = sorted(glob.glob(f"{PASTA_ENTRADA}/**/*.shp", recursive=True))
print("shapefiles encontrados:", len(arquivos))

for shp in arquivos:
    nome = os.path.basename(shp).replace(".shp", "").strip("_")
    try:
        g, corrigido = ler(shp)
    except Exception as e:
        print(f"\n{nome}: ERRO {str(e)[:150]}")
        continue

    print(f"\n=== {nome}")
    print("linhas:", len(g), "| tipo:", list(g.geom_type.unique())[:3])
    if corrigido:
        print("  (projeção definida à mão: confira no mapa)")
    print("colunas:", [c for c in g.columns if c != "geometry"])

    if g.geom_type.astype(str).str.contains("Line").all():
        print("  extensão total (km):", round(g.to_crs(31982).length.sum() / 1000, 1))
    g = g.to_crs(4326)

    g.to_file(f"{PASTA_SAIDA}/{nome}.geojson", driver="GeoJSON")

    tab = g.drop(columns="geometry")
    if (g.geom_type == "Point").all():
        tab["lat"], tab["lon"] = g.geometry.y, g.geometry.x
    tab.to_csv(f"{PASTA_SAIDA}/{nome}.csv", index=False)

print("\nPronto! Arquivos em:", PASTA_SAIDA)
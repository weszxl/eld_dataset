import time
import pandas as pd
import geopandas as gpd
from geopy.geocoders import ArcGIS

poa = [
    # --- 3 CENTROS POP ---
    {"categoria": "Centro POP", "nome": "Centro POP I - Santana", "endereco": "Avenida João Pessoa, 2384, Farroupilha, Porto Alegre, RS"},
    {"categoria": "Centro POP", "nome": "Centro POP II - Floresta", "endereco": "Rua Gaspar Martins, 114, Floresta, Porto Alegre, RS"},
    {"categoria": "Centro POP", "nome": "Centro POP III - Navegantes", "endereco": "Avenida França, 496, Navegantes, Porto Alegre, RS"},

    # --- 9 CREAS ---
    {"categoria": "CREAS", "nome": "CREAS Centro, Ilhas, Humaitá e Navegantes", "endereco": "Travessa do Carmo, 50, Cidade Baixa, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Glória, Cruzeiro e Cristal", "endereco": "Rua Professor Oscar Pereira, 2693, Glória, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Leste", "endereco": "Rua Porto Seguro, 261, Vila Ipiranga, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Lomba do Pinheiro", "endereco": "Rua Gervásio Braga, 642, Lomba do Pinheiro, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Noroeste", "endereco": "Rua Dom Diogo de Souza, 1300, Cristo Redentor, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Norte / Eixo Baltazar", "endereco": "Avenida Assis Brasil, 6755, Sarandi, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Partenon", "endereco": "Rua Barão do Amazonas, 1957, Partenon, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Restinga / Extremo Sul", "endereco": "Estrada João Antônio da Silveira, 2400, Restinga, Porto Alegre, RS"},
    {"categoria": "CREAS", "nome": "CREAS Sul / Centro Sul", "endereco": "Avenida Wenceslau Escobar, 2442, Cristal, Porto Alegre, RS"},

    # --- 23 CRAS ---
    {"categoria": "CRAS", "nome": "CRAS Centro", "endereco": "Rua José do Patrocínio, 780, Cidade Baixa, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Centro Sul", "endereco": "Avenida Cervantes, 255, Vila Nova, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Cristal", "endereco": "Rua Curupaiti, 27, Cristal, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Cruzeiro", "endereco": "Rua Dona Otília, 210, Santa Tereza, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Eixo Baltazar", "endereco": "Avenida Baltazar de Oliveira Garcia, 2132, Passo das Pedras, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Extremo Sul", "endereco": "Estrada Costa Gama, 719, Belém Novo, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Farrapos", "endereco": "Rua Maria Trindade, 115, Farrapos, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Glória", "endereco": "Rua Coronel Neves, 555, Medianeira, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Hípica", "endereco": "Rua Geraldo Tollens Linck, 235, Hípica, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Ilhas", "endereco": "Rua Capitão Coelho, 300, Arquipélago, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Leste I", "endereco": "Rua Jerusalém, 615, Bom Jesus, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Leste II", "endereco": "Rua Emílio Keidann, 50, Morro Santana, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Lomba do Pinheiro", "endereco": "Rua Jaime Rollemberg de Lima, 137, Lomba do Pinheiro, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Nordeste", "endereco": "Rua Irmão Ildefonso Luís, 210, Mário Quintana, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Noroeste", "endereco": "Rua Irene Capponi Santiago, 290, Vila Floresta, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Norte", "endereco": "Rua Paulo Gomes de Oliveira, 200, Sarandi, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Partenon", "endereco": "Rua Barão do Amazonas, 1957, Partenon, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Restinga", "endereco": "Estrada Chácara do Banco, 71, Restinga, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Restinga Velha", "endereco": "Rua Abolição, 415, Restinga, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS 5ª Unidade Restinga", "endereco": "Rua Arno Horn, 221, Restinga, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Santa Rosa", "endereco": "Rua Abelino Nicolau de Almeida, 330, Rubem Berta, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Sul", "endereco": "Avenida Guarujá, 190, Guarujá, Porto Alegre, RS"},
    {"categoria": "CRAS", "nome": "CRAS Timbaúva", "endereco": "Rua Sebastião Wolf, 1295, Mário Quintana, Porto Alegre, RS"},
]

geolocator = ArcGIS(timeout=15)

locations = []
for item in poa:
    loc = geolocator.geocode(item["endereco"])
    lat = round(loc.latitude, 6) if loc else None
    lon = round(loc.longitude, 6) if loc else None
    print(f"[OK] {item['nome']} -> ({lat}, {lon})")
    locations.append({**item, "latitude": lat, "longitude": lon})
    time.sleep(0.3)

df = pd.DataFrame(locations)

gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
    crs="EPSG:4326"
).to_crs("EPSG:4674")

gdf.to_file("assistencia_social_poa.gpkg", driver="GPKG")
df.to_csv("assistencia_social_poa.csv", index=False, encoding="utf-8-sig")

print("\n---------------")
print(df["categoria"].value_counts())
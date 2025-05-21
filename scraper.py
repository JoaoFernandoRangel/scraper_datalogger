import requests
import time
from datetime import datetime
import os
import json
from bs4 import BeautifulSoup


url = "http://200.137.71.136/channels.php"

# Garante que as pastas existam
os.makedirs("paginas", exist_ok=True)
os.makedirs("json_logs", exist_ok=True)


def extrair_tabela_para_json(html):
    soup = BeautifulSoup(html, "html.parser")
    linhas = soup.find_all("tr")

    dados = []
    timestamp = datetime.now()
    item0 = {"timeStamp": str(timestamp).strip(), "epoch": time.time()}

    dados.append(item0)
    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) != 6:
            continue
        item = {
            "tag": colunas[0].text.strip(),
            "nome": colunas[1].text.strip(),
            "valor": float(colunas[2].text.strip()),
            "unidade": colunas[3].text.strip(),
            "tipo": colunas[4].text.strip(),
            "logado": colunas[5].text.strip(),
        }
        dados.append(item)

    return {"dados_timestamp": dados}


def convert_csv(data):
    linha = ""
    valores = {}

    # Extrai todos os dados da lista
    for item in data["dados_timestamp"]:
        if "nome" in item and "valor" in item:
            valores[item["nome"]] = item["valor"]
        elif "timeStamp" in item:
            valores["timestamp_coleta"] = item["timeStamp"]

    # Define a ordem e as chaves que queremos extrair
    keys = [
        "timestamp_coleta",
        "T_MF4_IN",
        "T_MF4_OUT",
        "T_MM2_IN",
        "T_MM2_OUT",
        "T_BOILER100",
        "T_BOILER200",
        "T_IN",
        "Sinal_Vazao1",
    ]

    for key in keys:
        linha += f"{valores.get(key, '')},"

    return linha.rstrip(",")  # Remove a última vírgula


header = "timestamp_coleta,T_MF4_IN,T_MF4_OUT,T_MM2_IN,T_MM2_OUT,T_BOILER100,T_BOILER200,T_IN,Sinal_Vazao1"
try:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(f"csv/dados_{timestamp}.csv", "a", encoding="utf-8") as f:
        f.write(header + "\n")
    while True:
        response = requests.get(url)
        response.raise_for_status()
        # Extrai JSON
        json_data = extrair_tabela_para_json(response.text)
        timestampNew = json_data["dados_timestamp"][0]["timeStamp"]
        # json_filename = f"json_logs/dados_{timestamp}.json"
        # with open(json_filename, "w", encoding="utf-8") as f:                # json.dump(json_data, f, indent=4, ensure_ascii=False)
        toWrite = convert_csv(json_data)
        with open(f"csv/dados_{timestamp}.csv", "a", encoding="utf-8") as f:
            f.write(toWrite + "\n")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nCaptura interrompida pelo usuário.")

except requests.exceptions.RequestException as e:
    print(f"Erro ao acessar a página: {e}")

import requests
import time
from datetime import datetime
import os
import json
import threading
import queue
from bs4 import BeautifulSoup

url = "http://200.137.71.136/channels.php"

# Cria pastas necessárias
os.makedirs("paginas", exist_ok=True)
os.makedirs("json_logs", exist_ok=True)
os.makedirs("csv", exist_ok=True)

html_queue = queue.Queue()

header = "timestamp_coleta,T_MF4_IN,T_MF4_OUT,T_MM2_IN,T_MM2_OUT,T_BOILER100,T_BOILER200,T_IN,Sinal_Vazao1"
csv_filename = f"csv/dados_{datetime.now().strftime('%Y%m%d-%H%M%S')}.csv"

# Cria o CSV com cabeçalho
with open(csv_filename, "w", encoding="utf-8") as f:
    f.write(header + "\n")


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

    for item in data["dados_timestamp"]:
        if "nome" in item and "valor" in item:
            valores[item["nome"]] = item["valor"]
        elif "timeStamp" in item:
            valores["timestamp_coleta"] = item["timeStamp"]

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

    return linha.rstrip(",")


def thread_requisicao():
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_queue.put(response.text)
        except requests.exceptions.RequestException as e:
            print(f"[Requisição] Erro: {e}")
            time.sleep(1)


def thread_processamento():
    while True:
        html = html_queue.get()  # Bloqueia até ter item
        json_data = extrair_tabela_para_json(html)
        csv_line = convert_csv(json_data)

        with open(csv_filename, "a", encoding="utf-8") as f:
            f.write(csv_line + "\n")


# Criação e início das threads
t1 = threading.Thread(target=thread_requisicao, daemon=True)
t2 = threading.Thread(target=thread_processamento, daemon=True)

t1.start()
t2.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExecução interrompida pelo usuário.")

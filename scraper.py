import requests
import time
from datetime import datetime
import os
import json
from bs4 import BeautifulSoup

# URL da página
url = "http://200.137.71.136/channels.php"  # Substitua pelo IP real ou URL desejado

# Garante que as pastas existam
os.makedirs("paginas", exist_ok=True)
os.makedirs("json_logs", exist_ok=True)

def extrair_tabela_para_json(html):
    soup = BeautifulSoup(html, "html.parser")
    linhas = soup.find_all("tr")

    dados = []

    for linha in linhas:
        colunas = linha.find_all("td")
        if len(colunas) != 6:
            continue  # Ignora linhas que não têm 6 colunas

        item = {
            "nome": colunas[1].text.strip(),
            "valor": float(colunas[2].text.strip()),
            "unidade": colunas[3].text.strip(),
            "tipo": colunas[4].text.strip(),
            "logado": colunas[5].text.strip()
        }
        dados.append(item)

    return {"dados_timestamp": dados}

try:
    while True:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Salva o HTML
        html_filename = f"paginas/pagina_{timestamp}.html"
        response = requests.get(url)
        response.raise_for_status()
        with open(html_filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"✅ PHP salvo: {html_filename}")

        # Extrai JSON
        json_data = extrair_tabela_para_json(response.text)
        json_filename = f"json_logs/dados_{timestamp}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"✅ JSON salvo: {json_filename}")

        time.sleep(0.3)

except KeyboardInterrupt:
    print("\n⏹️ Captura interrompida pelo usuário.")

except requests.exceptions.RequestException as e:
    print(f"❌ Erro ao acessar a página: {e}")

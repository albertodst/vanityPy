import requests
import subprocess
import hashlib
import json
import time
import os
import re
from concurrent.futures import ProcessPoolExecutor

API_URL = os.environ.get('API_URL', 'https://api.btcpuzzle.info')
USER_TOKEN = os.environ.get('USER_TOKEN', '')
WALLET_ADDRESS = os.environ.get('WALLET_ADDRESS', '1EEq7exE91EUCLvC5s6PeecPmUomwA7GMy')
API_SENDER = os.environ.get('API_SENDER', '')
TARGET=os.environ.get('TARGET', '1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9')
PREFIX="00000000000000000000000000000000000000000000000"
PUZZLE_CODE = os.environ.get('PUZZLE_CODE', '67')
START_WITH = os.environ.get('START_WITH', '64')
GPU_ID = os.environ.get('GPU_ID', '0')
GPU_COUNT = os.environ.get('GPU_COUNT', '1')

def get_puzzle_data(puzzle_code, start_with):
    url = f"{API_URL}/hex/getv3?PuzzleCode={puzzle_code}&StartsWith={start_with}"
    headers = {"UserToken": USER_TOKEN, "WalletAddress": WALLET_ADDRESS}
    response = requests.get(url, headers=headers)
    print(response.text)
    data = response.text.split(":")
    #return data[1:]
    return data

def write_to_file(data, file_path):
    with open(file_path, 'w') as f:
        for item in data[1:]:
            f.write(item + '\n')
        f.write(TARGET + '\n')

def execute_command(command):
    subprocess.run(command, shell=True)

def calculate_sha256(hex_string):
    return hashlib.sha256(hex_string.encode('utf-8')).hexdigest()

def post_to_telegram_sender(hex_value, id):
    name = "GPU #" + str(id)
    url = API_SENDER
    headers = {"Status": "workerStarted", "HEX": hex_value, "Workeraddress": WALLET_ADDRESS, "Targetpuzzle": str(PUZZLE_CODE), "Workername": name}
    requests.post(url, headers=headers)

def post_key_to_telegram_sender(key, id):
    name = "GPU #" + str(id)
    url = API_SENDER
    headers = {"Status": "keyFound", "Privatekey": key, "Workeraddress": WALLET_ADDRESS, "Workername": name}
    requests.post(url, headers=headers)

def post_job_done_to_telegram_sender(range, id):
    name = "GPU #" + str(id)
    url = API_SENDER
    headers = {"Status": "rangeScanned", "Hex": range, "Workeraddress": WALLET_ADDRESS, "Workername": name, "Targetpuzzle": str(PUZZLE_CODE)}
    requests.post(url, headers=headers)

def main(id):
    addr_hex_dict = {}
    post_to_telegram_sender(START_WITH, id)
    while True:
        data = get_puzzle_data(PUZZLE_CODE, START_WITH)
        write_to_file(data, "../VanitySearch/in.txt")
        print(data)

        #Esegui il comando esterno
        subprocess.run(
         "(cd ../VanitySearch; ./vanitysearch -t 0 -gpu -gpuId {} -i in.txt -o out.txt --keyspace {}0000000000:+FFFFFFFFFF)".format(id, data[0]), 
         shell=True
        )

        # Leggi il file out.txt e calcola lo SHA256
        with open("../VanitySearch/out.txt", 'r') as f:
            lines = f.readlines()
            public_addr = None
            for line in lines:
               # Cerca la riga con "Public Addr"
               if "Public Addr:" in line:
                     public_addr = line.split("Public Addr:")[1].strip()
               
               # Cerca la riga con "Priv (HEX)" e cattura il valore esadecimale
               elif "Priv (HEX):" in line:
                     hex_value = re.search(r'([A-F0-9]{16,})', line)
                     if public_addr and hex_value:
                        addr_hex_dict[public_addr] = hex_value.group(0)

        # Stampa o salva il risultato come JSON
        if TARGET in addr_hex_dict:
            privateKey=addr_hex_dict[TARGET]
            post_key_to_telegram_sender(privateKey, id)
            print("Key exists in the dictionary.")
            os.remove("../VanitySearch/out.txt")
            break
        else:
            combined_hex = PREFIX+PREFIX.join(addr_hex_dict.values())
            sha256 = calculate_sha256(combined_hex)
            url = f"{API_URL}/hex/flag"
            headers = {"HEX": data[0], "WalletAddress": WALLET_ADDRESS, "Targetpuzzle": str(PUZZLE_CODE), "ProofKey": sha256}
            response = requests.post(url, headers=headers)
            # Controlla la risposta e decide se continuare
            if response.status_code == 200:
                  # Continua con il prossimo ciclo
                  post_job_done_to_telegram_sender(data[0], id)
                  pass
            else:
                  print("Errore nell'invio del risultato")
                  break

if __name__ == "__main__":
    with ProcessPoolExecutor() as executor:
        executor.map(main, range(int(GPU_COUNT)))
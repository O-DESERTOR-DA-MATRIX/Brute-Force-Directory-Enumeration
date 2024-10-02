import requests
import argparse
import pyfiglet
import concurrent.futures
import sys
import queue
import os

# Cores ANSI mais suaves
COLOR_OK = "\033[32m"  # Verde
COLOR_FORBIDDEN = "\033[33m"  # Amarelo mais suave
COLOR_RESET = "\033[0m"  # Reseta a cor

# Função para exibir o texto e o símbolo do pinguim
def display_intro():
    result = pyfiglet.figlet_format("S4V10R")
    print(result)
    print(r"""
            .--.       
           |o_o |      
           |:_/ |      
          //   \ \     
         (|     | )    
        /'\_   _/`\   
        \___)=(___/   
    """)
    print("\n")

# Função para verificar uma URL e retornar se novos subdiretórios foram encontrados
def check_single_url(ip, endpoint, checked_urls, output_file):
    url = f"{ip}/{endpoint}"
    if url in checked_urls:  # Ignora URLs já verificadas
        return False

    try:
        r = requests.get(url, timeout=1.5)
        checked_urls.add(url)  # Adiciona URL ao conjunto de verificados

        if r.status_code == 200:
            message = f"{COLOR_OK}200 ==> OK: {url}{COLOR_RESET}"
            print(message)
            if output_file:
                with open(output_file, 'a') as f:  # Salva em modo append
                    f.write(f"200 ==> OK: {url}\n")  # Escreve a mensagem no arquivo sem cor
            return True  # Retorna True se o subdiretório foi encontrado e é válido
        elif r.status_code == 403:
            message = f"{COLOR_FORBIDDEN}403 ==> FB: {url}{COLOR_RESET}"
            print(message)
            if output_file:
                with open(output_file, 'a') as f:  # Salva em modo append
                    f.write(f"403 ==> FB: {url}\n")  # Escreve a mensagem no arquivo sem cor
            return False
    except requests.RequestException:
        return False

# Função para verificar URLs usando um pool de threads e fila
def checkurl(ip, wordlist, num_threads, output_file):
    try:
        with open(wordlist, 'r') as file:
            base_endpoints = file.read().split()

            if num_threads == 0:
                num_threads = 10  # Define um padrão de 10 threads se não for especificado

            # Usando uma fila para controlar a quantidade de threads
            q = queue.Queue()

            # Adiciona os endpoints à fila
            for endpoint in base_endpoints:
                q.put(endpoint)

            # Conjunto para URLs verificadas
            checked_urls = set()
            # Lista para armazenar novos subdiretórios encontrados
            found_directories = []

            while not q.empty() or found_directories:
                if found_directories:  # Se houver novos subdiretórios encontrados, os adiciona à fila
                    for directory in found_directories:
                        q.put(directory)
                    found_directories.clear()  # Limpa a lista após adicionar à fila

                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = {executor.submit(check_single_url, ip, endpoint, checked_urls, output_file): endpoint for endpoint in list(q.queue)}

                    for future in concurrent.futures.as_completed(futures):
                        endpoint = futures[future]
                        if future.result():  # Se a URL foi encontrada
                            found_directories.append(endpoint)

                # Aguarda até que todas as tarefas sejam concluídas
                q.join()

            print("Nenhum novo subdiretório encontrado. Processo encerrado.")

    except FileNotFoundError:
        print("Wordlist path is invalid. Check your input and try again.")

if __name__ == "__main__":
    display_intro()

    parser = argparse.ArgumentParser(description='Check URLs from a wordlist.')
    parser.add_argument('-u', '--url', required=True, help='The base URL (with http/https)')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to the wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=0, help='Number of threads to use (0 for default 10 threads)')
    parser.add_argument('-o', '--output', help='Path to the output file (will be created if it does not exist)')

    args = parser.parse_args()

    print(f"URL argument: {args.url}")
    print(f"Wordlist argument: {args.wordlist}")
    print(f"Number of threads: {args.threads}\n")
    print("------------------------------------------------------------------------------")

    if args.threads < 0 or args.threads > 100:
        print("Error: The number of threads must be between 0 and 100.")
        sys.exit(1)

    # Cria o arquivo de saída se não existir
    if args.output:
        if not os.path.exists(args.output):
            open(args.output, 'w').close()  # Cria um novo arquivo vazio

    checkurl(args.url, args.wordlist, args.threads, args.output)

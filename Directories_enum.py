import requests
import argparse
import pyfiglet
import threading
import sys

# Função para exibir o texto e o símbolo do pinguim
def display_intro():
    # Gera o texto "S4V10R" em formato de arte
    result = pyfiglet.figlet_format("S4V10R")
    print(result)

    # Adiciona o símbolo do pinguim
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

# Função para verificar uma URL
def check_single_url(ip, endpoint, semaphore):
    with semaphore:  # Limita o número de threads ativas
        url = f"https://{ip}/{endpoint}"
        try:
            r = requests.get(url, timeout=1.5)
            if r.status_code == 200:
                print(f"200 ==> OK: {url}")
            elif r.status_code == 403:
                print(f"403 ==> Forbidden URL: {url} (403 code error)")
        except:
            pass
            
# Função para verificar URLs em múltiplas threads
def checkurl(ip, wordlist, num_threads):
    try:
        with open(wordlist, 'r') as file:
            reading = file.read()
            splitting = reading.split()
            
            # Se num_threads for 0, use 1 thread por padrão
            if num_threads == 0:
                num_threads = 1
            
            semaphore = threading.Semaphore(num_threads)  # Limita o número de threads ativas
            threads = []
            for i in splitting:
                # Cria uma thread para cada URL a ser verificada
                thread = threading.Thread(target=check_single_url, args=(ip, i, semaphore))
                threads.append(thread)
                thread.start()  # Inicia a thread
            
            # Aguarda todas as threads terminarem
            for thread in threads:
                thread.join()

    except FileNotFoundError:
        print("Wordlist path is invalid. Check your input and try again.")

if __name__ == "__main__":
    display_intro()  # Exibir introdução com "S4V10R" e o pinguim

    # Criação do parser de argumentos
    parser = argparse.ArgumentParser(description='Check URLs from a wordlist.')
    
    # Definindo os argumentos opcionais para a URL, a wordlist e o número de threads
    parser.add_argument('-u', '--url', required=True, help='The base URL (without http/https)')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to the wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=0, 
                        help='Number of threads to use (0 for single-threaded) [default: 0]')

    # Parseando os argumentos
    args = parser.parse_args()

    # Verificação para garantir que os argumentos estão sendo passados corretamente
    print(f"URL argument: {args.url}")
    print(f"Wordlist argument: {args.wordlist}")
    print(f"Number of threads: {args.threads}\n")
    print("------------------------------------------------------------------------------")
    


    # Verificação do número de threads
    if args.threads < 0 or args.threads > 100:
        print("Error: The number of threads must be between 0 and 100.")
        sys.exit(1)  # Sai do programa com um código de erro
   
    checkurl(args.url, args.wordlist, args.threads)

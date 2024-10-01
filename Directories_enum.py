import requests
import sys
import pyfiglet

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

# Função para verificar URLs
def checkurl(ip, wordlist):
    try:
        with open(wordlist, 'r') as file:
            reading = file.read()
            splitting = reading.split()
            
            for i in splitting:
                url = f"https://{ip}/{i}"
                try:
                    r = requests.get(url, timeout=1.5)
                    
                    if r.status_code == 200:
                        print(f"URL found: {url}")
                    elif r.status_code == 403:
                        print(f"Forbidden URL: {url} (403 code error)")

                except requests.exceptions.RequestException as e:
                    print(f"Error accessing {url}: {e}")
                
    except FileNotFoundError:
        print("Wordlist path is invalid. Check your input and try again.")           

if __name__ == "__main__":
    display_intro()  # Exibir introdução com "S4V10R" e o pinguim
    
    ip = input("Type your URL or IP (without http/https): ")
    wordlist = input("Type your wordlist path: ")
    
    checkurl(ip, wordlist)

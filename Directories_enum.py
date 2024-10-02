import requests
import argparse
import pyfiglet
import concurrent.futures
import sys
import queue
import os

# Lighter ANSI colors
COLOR_OK = "\033[32m"  # Green
COLOR_FORBIDDEN = "\033[33m"  # Softer yellow
COLOR_RESET = "\033[0m"  # Resets color

# Function to display the banner and penguin symbol
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

# Function to check a URL and return if new subdirectories are found
def check_single_url(ip, endpoint, checked_urls, output_file):
    url = f"{ip}/{endpoint}"
    if url in checked_urls:  # Skips already checked URLs
        return False

    try:
        r = requests.get(url, timeout=1.5)
        checked_urls.add(url)  # Adds URL to the set of checked ones

        if r.status_code == 200:
            message = f"{COLOR_OK}200 ==> OK: {url}{COLOR_RESET}"
            print(message)
            if output_file:
                with open(output_file, 'a') as f:  # Saves in append mode
                    f.write(f"200 ==> OK: {url}\n")  # Writes the message without color
            return True  # Returns True if the subdirectory is found and valid
        elif r.status_code == 403:
            message = f"{COLOR_FORBIDDEN}403 ==> FB: {url}{COLOR_RESET}"
            print(message)
            if output_file:
                with open(output_file, 'a') as f:  # Saves in append mode
                    f.write(f"403 ==> FB: {url}\n")  # Writes the message without color
            return False
    except requests.RequestException:
        return False

# Function to check URLs using a thread pool and queue
def checkurl(ip, wordlist, num_threads, output_file):
    try:
        with open(wordlist, 'r') as file:
            base_endpoints = file.read().split()

            if num_threads == 0:
                num_threads = 10  # Default to 10 threads if not specified

            # Using a queue to control the number of threads
            q = queue.Queue()

            # Add endpoints to the queue
            for endpoint in base_endpoints:
                q.put(endpoint)

            # Set for checked URLs
            checked_urls = set()
            # List to store newly found subdirectories
            found_directories = []

            while not q.empty() or found_directories:
                if found_directories:  # If new subdirectories are found, add them to the queue
                    for directory in found_directories:
                        q.put(directory)
                    found_directories.clear()  # Clear the list after adding to the queue

                with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                    futures = {executor.submit(check_single_url, ip, endpoint, checked_urls, output_file): endpoint for endpoint in list(q.queue)}

                    for future in concurrent.futures.as_completed(futures):
                        endpoint = futures[future]
                        if future.result():  # If the URL was found
                            found_directories.append(endpoint)

                # Wait for all tasks to finish
                q.join()

            print("No new subdirectories found. Process ended.")

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

    # Creates the output file if it doesn't exist
    if args.output:
        if not os.path.exists(args.output):
            open(args.output, 'w').close()  # Creates an empty new file

    checkurl(args.url, args.wordlist, args.threads, args.output)

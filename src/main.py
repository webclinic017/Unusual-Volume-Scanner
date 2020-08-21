import pathlib
import os, sys
from contextlib import contextmanager
import scanner as scn
import plotter as plt

DATA_PATH = 'data/ticker_urls.txt'
CURR_PATH = pathlib.Path(__file__).parent.absolute().parents[0]
TXT_PATH = os.path.join(CURR_PATH, DATA_PATH)

#supress output to console
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def ui():
    print("********WELCOME TO UNUSUAL VOLUME SCANNER*********")
    ticker_urls = scn.readURLs(TXT_PATH)
    print("-" * 52)
    ticker_bucket = []
    while True:
        print("What would you like to do?")
        print("1. Scan the Market")
        print("2. Plot Stock Volume")
        print("3. Quit")
        selection = input("Enter Selection: ")
        if selection == "1":
            #reset watchlist
            ticker_bucket = []
            ticker_bucket = scn.scanMarket(ticker_urls, ticker_bucket)
        elif selection == "2":
            plt.plotUI(ticker_bucket)
        elif selection == "3":
            break
        else:
            continue

if __name__ == "__main__":
    ui()

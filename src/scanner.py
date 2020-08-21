import pathlib
import os
import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
import concurrent.futures
import yfinance as yf
import main
import math
from multiprocessing import Lock
import random

#prints closing asterik block using ticker length
def printClosingAsterik(ticker_len, padding):
    print("*" * (ticker_len + padding ))

#prints ticker, current volume and 3 month average volume
def printVolumeData(ticker, curr_vol, mean_vol,):
    print("*************" + ticker + "*************")
    print("Current Volume: " + curr_vol)
    print("Mean Volume: " + mean_vol)
    printClosingAsterik(len(ticker), 26)

#reads in text file with urls and returns list
def readURLs(file_path):
    with open(file_path, 'r') as data:
        urls = data.readlines()[0].split(',')
    return urls

#get html from url
async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

#add fetch function to event loop
async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(session, url))
        tasks.append(task)
    results = await asyncio.gather(*tasks)
    return results

#return html for urls
async def getHTMLs(urls):
    async with aiohttp.ClientSession() as session:
        htmls = await fetch_all(session, urls)
    return htmls

#extracts 3 month average volume
def extractVol(html):
    soup = BeautifulSoup(html, 'html.parser')
    ticker = soup.find('h1', attrs={"data-reactid": "7"})
    if ticker is None:
        ticker = ""
    else:
        ticker = ticker.text
        ticker = ticker[ticker.find("(")+1:ticker.find(")")]
    vol_data = [selection.find('span').text for selection in soup.find_all('td',
        attrs={"data-test": ["TD_VOLUME-value", "AVERAGE_VOLUME_3MONTH-value"]})]
    if len(vol_data) == 0:
        vol_data = ["", ""]
    toReturn = {'ticker': ticker, 'curr_vol': vol_data[0], 'mean_vol': vol_data[1]}
    return toReturn

#return 3 month 5x stdev
def getStDev(ticker):
    with main.suppress_stdout():
        data = yf.Ticker(ticker).history(period = '3mo')['Volume']
    #no data available
    if data.empty:
        return None
    else:
        std = data.std()
        #check if std returns NaN
        if math.isnan(std):
            return None
        else:
            return int(std)

#returns true if current volume exceeds std. above 3 month mean_vol
def printResult(curr_vol, mean_vol, std, multiplier):
    curr_vol = int(curr_vol.replace(",", ""))
    exceed_vol = int(mean_vol.replace(",", "")) + (std*multiplier)
    if curr_vol > exceed_vol:
        return True
    else:
        return False

#determines if result is printed
def controlPrint(result, multiplier):
    #volume data is not available
    if 'N/A' in result.values() or "" in result.values():
        return
    std = getStDev(result['ticker'])
    #std returns NaN float
    if std == None:
        return
    if printResult(result['curr_vol'], result['mean_vol'], std, multiplier):
        printVolumeData(result['ticker'], result['curr_vol'], result['mean_vol'])
        return result['ticker']

#runs extract volume in parallel
def processHTML(htmls, multiplier, ticker_bucket):
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = executor.map(extractVol, htmls)
    for result in results:
        ticker = controlPrint(result, multiplier)
        if ticker is None:
            pass
        else:
            ticker_bucket.append(ticker)
    return ticker_bucket

#controls volume detector module ui
def scanMarket(ticker_urls, ticker_bucket):
    print("***********VOLUME SCANNER MODULE***********")
    print("Stock whose volume has exceeded the 3-month \navg. by X Std. are printed to the console.")
    print("Choose from the options below.")
    print("1. Randomly scan 100 stocks on the market")
    print("2. Full market scan (takes about 25 minutes)")
    while True:
        selection = input("What would you like to do?: ")
        if selection in ["1", "2"]:
            break
    while True:
        multiplier = input("Enter sensitivity of detector \n(Integer value between 0-10) \n10 being most sensitive: ")
        if multiplier in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"}:
            multiplier = int(multiplier)
            break;
    print("SCANNING THE MARKET...")
    print("-" * 43)
    if selection == "1":
        ticker_urls = random.sample(ticker_urls, 100)
        htmls = asyncio.run(getHTMLs(ticker_urls))
    else:
        htmls = asyncio.run(getHTMLs(ticker_urls))
    ticker_bucket = processHTML(htmls, multiplier, ticker_bucket)
    if len(ticker_bucket) != 0:
        print("TICKERS ADDED TO WATCHLIST")
    else:
        print("NO UNUSUAL VOLUME FOUND")
    return ticker_bucket

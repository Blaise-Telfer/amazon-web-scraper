import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from pathlib import Path
import requests


def get_url(search_term):
  template = "https://www.amazon.com/s?k={}&ref=sr_pg_2"
  search_term = search_term.replace(" ", "+")
  
  url = template.format(search_term)
  url += "&page{}"
  
  return url

def extract_record(item):
  #description and url
  atag = item.h2.a
  description = atag.text.strip()
  url = "https://www.amazon.com" + atag.get("href")
  
  #price
  try:
    price_parent = item.find("span", "a-price")
    price = price_parent.find("span", "a-offscreen").text
  except AttributeError:
    return
  
  #rating
  try:
    rating = item.i.text
    rating_count = item.find("span", {"class": "a-size-base"}).text
  except AttributeError:
    rating = ""
    rating_count = ""
  
  result = (description, price, rating, rating_count, url)
  return result

def main(search_term):
  DRIVER_PATH = str(Path("geckodriver").resolve())
  browser = webdriver.Firefox(executable_path=DRIVER_PATH)
  
  Records = []
  url = get_url(search_term)
  
  for page in range(1, 21):
    browser.get(url.format(page))
    soup = BeautifulSoup(browser.page_source, "html.parser")
    results = soup.find_all("div", {"data-component-type": "s-search-result"})
	
    for item in results:
      record = extract_record(item)
      if record:
        Records.append(record)
  
  browser.close()
  
  with open(f"{search_term} results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Description", "Price", "Rating", "Review Count", "URL"])
    
    for i in range(len(Records)):
      writer.writerow(Records[i])
  
  print(f"Saved {search_term} results.csv successfully.")

print("What item would you like to search Amazon for? ")
search_term = input(">")
print(f"Searching for {search_term}...")

main(search_term)
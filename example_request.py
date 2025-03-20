import requests
import bs4
import lxml 

res = requests.get("https://example.com")

soup = bs4.BeautifulSoup(res.text,"lxml")

print(soup.select('title')[0].getText())
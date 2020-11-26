#!/usr/bin/env python3
import requests
import calendar
import typing
import logging
from json import dumps
from datetime import datetime
from bs4 import BeautifulSoup

base_url = 'http://eoddata.com/stocklist'
logger = logging.getLogger()

class Hydrator:

  def __init__(self) -> None:
    homepage = requests.get(base_url+'/AMEX/D.htm').text
    soup = BeautifulSoup(homepage,'lxml')
    self.__exchanges = [opt['value'] for opt in soup.find_all('option')]

  @property
  def exchanges(self) -> typing.List[str]:
    return self.__exchanges

  @staticmethod
  def a_to_z() -> typing.List[str]:
    return [chr(x) for x in range(65,65+26)]

  def fetch_all(self):
    results = {}
    for exchange in self.exchanges:
      for page in Hydrator.a_to_z():
        page_values = self.fetch_page(exchange,page)
        results.update(page_values)

    return results

  def fetch_page(self, exchange:str, page:str) -> dict:
    url = self.__construct_url(exchange,page)
    logging.debug('Fetching '+url)

    page_values = self.__parse_page(url)
    return page_values

  def __construct_url(self, exchange:str, page:str) -> str:
    return '{base_url}/{exchange}/{page}.htm'.format(
      base_url=base_url,
      exchange=exchange,
      page=page)
    
  def __parse_page(self,url:str) -> dict:
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')
    values = {}
    for row_class in ['ro','re']:
      rows = soup.find_all('tr', attrs={'class':row_class})
      for row in rows:
          cells = row.find_all('td')
          symbol = cells[0].text
          name = cells[1].text
          values[symbol] = name
    return values

# Entry point for directly running
if __name__ == "__main__":
  hydrator = Hydrator()
  with open('mappings.json','w') as file:
    results = hydrator.fetch_all()
    file.write(dumps(results, indent=2))

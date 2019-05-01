"""
Class for parsing product web-page
"""

import requests
import re
from bs4 import BeautifulSoup
import json


class ProductParser:
    def __init__(self, link):
        """
        Creating a parser by and link
        :param link: link to product
        """
        self.link = link
        # Open link
        response = requests.get(link)
        # Create dict {[property ids]: price}
        json_prices = re.findall(r'skuProducts=(\[{.*}\])', response.text)
        if json_prices:
            try:
                self.prices = {tuple(sorted(x['skuPropIds'].split(','))):
                               x['skuVal']['actSkuMultiCurrencyCalPrice']
                               for x in json.loads(json_prices[0])}
            except KeyError:
                self.prices = {tuple(sorted(x['skuPropIds'].split(','))):
                               x['skuVal']['skuMultiCurrencyCalPrice']
                               for x in json.loads(json_prices[0])}
        else:
            self.prices = {}

    @property
    def properties(self):
        """
        Create a dict of properties
        """
        response = requests.get(self.link)
        soup = BeautifulSoup(response.text, 'lxml')
        sections = soup.find_all('dl', {'class': 'p-property-item'})
        properties_raw = {x.find('dt').text[:-1]: x.find_all('li')
                          for x in sections}
        properties = {}
        for key, value in properties_raw.items():
            if not value:
                continue
            res_value = {x.find('a').get('data-sku-id'):
                         x.find('span').get_text()
                         for x in value if x.find('span')}
            res_value.update({x.find('a').get('data-sku-id'):
                              x.find('a').get('title')
                              for x in value if x.find('a').get('title')})
            properties[key] = res_value
        return properties

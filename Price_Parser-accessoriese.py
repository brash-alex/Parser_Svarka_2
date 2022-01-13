import requests
from bs4 import BeautifulSoup
from loguru import logger
import re
import csv


class Site_parser(object):

    def __init__(self):
        self.base_url = 'https://svarog-rf.ru/'
        self.headers = requests.utils.default_headers()
        self.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'})


    def __get_soup(self, url_end):
        logger.debug(self.base_url + url_end)
        response = requests.get(self.base_url + url_end, headers=self.headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        else:
            return False


    def _get_categori_link(self):
        url_end = 'accessories'
        soup = self.__get_soup(url_end)
        rezalt = soup.find('div', class_='view-content').find_all('span', class_='field-content')
        return rezalt


    def _get_produkt_urls(self, url):
        soup = self.__get_soup(url)
        rezalt = soup.find('div', class_='view-products').find_all('h3')
        #logger.debug(rezalt)
        produkt_urls = []

        for item in rezalt:
            produkt_urls.append(item.find('a').get('href'))

        return produkt_urls

    def _get_produkt_info(self, url, cat_name):
        soup = self.__get_soup(url)
        pr = soup.find('div', id='col1')

        produkt_name = pr.find('h1').get_text()
        articul =   pr.find('div', class_='field field-name-field-art field-type-text field-label-inline clearfix').\
            findNext('div', class_='field-item even').get_text()

        produkt_price = str(pr.find('div', class_='field field-name-field-price field-type-number-integer field-label-above').\
            findNext('div', class_='field-item even').get_text())

        logger.debug(f"{produkt_name}  {articul}  {produkt_price}  {'ПРОДУКЦИЯ, ТМ СВАРОГ, Сопутствующие товары, ' + str(cat_name)} ")

        # prod_discr = prod_discr.replace(short_prod_discr, '.')

        return produkt_name, articul, produkt_price

    def have_thise_produkt_or_not(self, url):
        soup = self.__get_soup(url)
        rezalt = soup.find('div', class_='view-empty')
        logger.debug(rezalt)
        if rezalt:
            logger.debug("keine Produkte")
            return False

        else:
            logger.debug("es gibt Ware")
            return True






def write_items_in_file(data, path):
    name = ['Имя', 'Артикул', 'Базовая цена']
    with open (path, 'w', newline='', encoding="UTF-8") as file:
       print(' ; '.join(str(l) for l in name), file=file, sep="\n")
       for produkt in data:
           print(' ; '.join(str(l) for l in produkt), file=file, sep="\n")








def start():
    pars = Site_parser()
    ul = pars._get_categori_link()
    logger.debug(ul)
    i = 0
    all_produkts = []
    for item in ul:
        logger.info(item.find('a').get('href'))
        logger.info(item.find('a').get_text())
        i += 1
        logger.warning(item.find('a').get('href'))
        pagination_num = 0
        url_prod_pages = item.find('a').get('href') + f"?page={pagination_num}"
        logger.debug(url_prod_pages)

        while pars.have_thise_produkt_or_not(url_prod_pages):
            produkt_urls = pars._get_produkt_urls( url_prod_pages)

            for prod_url in produkt_urls:
                all_produkts.append(pars._get_produkt_info(prod_url, item.find('a').get_text()) )

            pagination_num += 999999999999999991
            url_prod_pages = item.find('a').get('href') + f"?page={pagination_num}"


        if i>999999999999991:
                break


    logger.debug(all_produkts)
    write_items_in_file(all_produkts, 'rezalt/priceUpdate_accessoriese.csv')















start()
import requests
from bs4 import BeautifulSoup
from loguru import logger
import re
import csv


class Site_parser(object):

    def __init__(self):
        self.base_url = 'https://svarog-rf.ru'
        self.headers = requests.utils.default_headers()
        self.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'})


    def __get_soup(self, url_end):
        # logger.debug(self.base_url + url_end)
        response = requests.get(self.base_url + url_end, headers=self.headers)
        if response.status_code == 200:
            logger.info(f"status_code == 200:")
            return BeautifulSoup(response.text, 'html.parser')
        else:
            return False


    def _get_categori_link(self, url_end):
        soup = self.__get_soup(url_end)
        pre_rezalt = soup.find('div', class_='view-content').find_all('span', class_='field-content')
        logger.debug(pre_rezalt)
        rezalt = {}
        for item in pre_rezalt:
            rezalt[item.find('a').get_text()] = (item.find('a').get('href'))
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

        produkt_name = pr.find('h1').get_text().replace(';', '.')
        articul =   pr.find('div', class_='field field-name-field-art field-type-text field-label-inline clearfix').\
            findNext('div', class_='field-item even').get_text()

        produkt_price = str(pr.find('div', class_='field field-name-field-price field-type-number-integer field-label-above').\
            findNext('div', class_='field-item even').get_text())

        logger.debug(f"{produkt_name}  {articul}  {produkt_price}  {str(cat_name)} ")
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


    def _get_subcategori_link(self, url):
        urls = None

        soup = self.__get_soup(url)
        find_sub_category =  soup.find('div', class_='panel-pane pane-views-panes pane-cats-panel-pane-4 cat-subcats')
        if find_sub_category:
            urls = find_sub_category.find_all('a')
        # logger.info(urls)
        return urls



def write_items_in_file(data, path):
    name = ['Имя', 'Артикул', 'Базовая цена']
    with open (path, 'w', newline='', encoding="UTF-8") as file:
       print(' ; '.join(str(l) for l in name), file=file, sep="\n")
       for produkt in data:
           print(' ; '.join(str(l) for l in produkt), file=file, sep="\n")


def try_too_find_subcat(cat_urls, pars):
    urls_for_delit = {}
    subCat_url_for_add = {}
    for name in cat_urls:

        i = pars._get_subcategori_link(cat_urls[name])
        # logger.debug(i)
        if i:
            urls_for_delit[name] = cat_urls[name]
            for url1 in i:
                subCat_url_for_add[url1.get_text()] = url1.get('href')
    return subCat_url_for_add, urls_for_delit


def get_final_category_urls(subCat_url_for_add, urls_for_delit, cat_urls):
    for item in urls_for_delit:
        del cat_urls[item]
    cat_urls.update(subCat_url_for_add)
    return cat_urls



def start():
    pars = Site_parser()
    urls_main_categories = {'Расходные материалы':'/consumables'}
    all_produkts = []
    for categori in urls_main_categories:
        cat_urls = pars._get_categori_link(urls_main_categories[categori])
        subCat_url_for_add, urls_for_delit  = try_too_find_subcat(cat_urls, pars)
        final_cat_urls = get_final_category_urls(subCat_url_for_add, urls_for_delit, cat_urls)

        for jast_cat_url in final_cat_urls:
            pagination_num = 0
            url_prod_pages = final_cat_urls[jast_cat_url] + f"?page={pagination_num}"
            logger.debug(url_prod_pages)

            while pars.have_thise_produkt_or_not(url_prod_pages):
                produkt_urls = pars._get_produkt_urls(url_prod_pages)

                for prod_url in produkt_urls:
                    logger.error(
                        " НЕ верно генерится название категориии!!! вместо названия вставляется урл!! кусок урла")
                    all_produkts.append(pars._get_produkt_info(prod_url, jast_cat_url))

                pagination_num += 1
                url_prod_pages = final_cat_urls[jast_cat_url] + f"?page={pagination_num}"
        logger.debug(all_produkts)
        write_items_in_file(all_produkts, 'rezalt/priceUpdate_consumables.csv')


start()
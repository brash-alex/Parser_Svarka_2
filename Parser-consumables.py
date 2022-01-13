import requests
from bs4 import BeautifulSoup
from loguru import logger
import re
import csv

product_in_site = ['00000093557', '00000092570', '00000094306', '00000096552', '00000094308', '00000096664', '00000096533',
                   '00000096420', '00000095727', '00000095883', '00000098556', '00000098557', '00000092563', '00000091096',
                   '00000097992', '00000095726', '00000095882', '00000097984', '00000095710', '00000097886', '00000097993',
                   '00000095490', '00000090921', '00000090920', '00000087881', '00000095492', '00000095994', '00000095487',
                   '00000095489', '00000095493', '00000092546', '00000090047', '00000091580', '00000091581', '00000094503',
                   '00000091097', '00000085213', '00000096877', '00000092748', '00000092661', '00000096534', '00000096535',
                   '00000085215', '00000091307', '00000096553', '00000091308', '00000093244', '00000090925', '00000096629',
                   '00000095484', '00000087777', '00000090962', '00000092681', '00000091014', '00000090963', '00000097807',
                   '00000090964', '00000091015', '00000094495', '00000096860', '00000088240', '00000096426', '00000094596',
                   '00000087283', '00000094602', '00000087289', '00000094599', '00000095748', '00000087286', '00000094605',
                   '00000088201', '00000087292', '00000088207', '00000088210', '00000088213', '00000088374', '00000088204',
                   '00000097798', '00000094614', '00000087256', '00000087260', '00000094610', '00000087272', '00000094612',
                   '00000087268', '00000087277', '00000088183', '00000088185', '00000088181', '00000092623', '00000098062',
                   '00000098272', '00000098063', '00000098271', '00000098270', '00000098269', '00000098268', '00000098266',
                   '00000098267', '00000096049', '00000098265', '00000098264', '00000096047', '00000096048', '00000096046',
                   '00000098263', '00000096039', '00000096044', '00000096041', '00000096043', '00000096040', '00000096042',
                   '00000096045', '00000097909', '00000097920', '00000097919', '00000097917', '00000097914', '00000093694',
                   '00000094358', '00000087296', '00000087300', '00000087297', '00000087298', '00000087302', '00000097126',
                   '00000097125', '00000087304', '00000092011', '00000092013', '00000088634', '00000098157', '00000094200',
                   '00000094203', '00000094201', '00000094204', '00000094205', '00000094206', '00000094475', '00000094476',
                   '00000094199', '00000094208', '00000094209', '00000094210', '00000094207', '00000094224', '00000094159',
                   '00000094157', '00000094160', '00000094158', '00000094180', '00000094175', '00000094170', '00000094169',
                   '00000095653', '00000094473', '00000096528', '00000096527', '00000094474', '00000095654', '00000094182',
                   '00000094177', '00000094183', '00000094178', '00000094181', '00000094176', '00000094750', '00000095655',
                   '00000095656', '00000095657']

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
        if articul in product_in_site:
            logger.warning(f"Товар уже есть на сайте, не будет добавлятся")
            return "", "", "", "", "", "", ""

        produkt_price = str(pr.find('div', class_='field field-name-field-price field-type-number-integer field-label-above').\
            findNext('div', class_='field-item even').get_text())
        try:
            prod_discr2 = pr.find('div',
                                 class_='field field-name-body field-type-text-with-summary field-label-hidden').find(
                'div', class_='field-items').find()
            prod_discr = prod_discr2#.replace('\n\t\t\t\t', ' ').replace('\n', ' ').replace(';', '.')
        except Exception as ex:
            logger.error(ex)
            prod_discr = 'Подробное описание товар появится позже'
        d = ''
        if not type(prod_discr) == str:
            for str1 in prod_discr:
                d=d+str(str1).replace('\n\t\t\t\t', ' ').replace('\n', ' ').replace(';', '.')
            prod_discr = d
        try:
            short_prod_discr = pr.find('div', class_='field field-name-body field-type-text-with-summary field-label-hidden').find('div', class_='field-item even').find()
            short_prod_discr = short_prod_discr.get_text().replace('\n\t\t\t\t', ' ').replace('\n', ' ').replace(';', '.')
        except Exception as ex:
            logger.error(ex)
            short_prod_discr = 'Краткое Описание товар появится позже'
        logger.debug(pr.find('div', class_='field field-name-field-images field-type-image field-label-hidden').find_all('a'))
        prod_images = ''
        for img in pr.find('div', class_='field field-name-field-images field-type-image field-label-hidden').find_all('a'):
            prod_images =  prod_images  + img.get('href') + ', '
        if prod_images:
            pass
        else:
            prod_images = "no image "
        logger.debug(f"{produkt_name}  {articul}  {produkt_price} {short_prod_discr} {prod_discr} {prod_images} {str(cat_name)} ")
        return produkt_name, articul, produkt_price, short_prod_discr, prod_discr, prod_images, str(cat_name)


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
    name = ['Имя', 'Артикул', 'Базовая цена', 'Краткое описание', 'Описание', 'images', 'Категории']
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
        write_items_in_file(all_produkts, 'rezalt/files_uploads_consumables.csv')


start()
import urllib.request
import requests
from bs4 import BeautifulSoup
import csv
import time
from selenium import webdriver
import random

def load_base(pid):
    try:
        fname = r'files/' + '3dbase' + '.csv'
        url = 'https://www.3djake.com/3d-printer-filaments?page='+str(pid)
        html = urllib.request.urlopen(url, timeout=100)
        browser = webdriver.Firefox()
        browser.get(url)
        browser.refresh()
        browser.refresh()
        browser.execute_script("window.onblur = function() { window.onfocus() }") 
        source_data = browser.page_source
        soup = BeautifulSoup(source_data,features="html5lib")
        browser.close()
        #soup = BeautifulSoup(html, 'html5lib') # instead of html.parser
        list_goods = soup.find_all("li", {"class": "product-v2"})
        filrow = []

        for good in list_goods:
            element = good.find("div", {"class": "product__title"})
            element2 = good.find("div", {"class": "product__footer"})
            g_name = element.find("a").text
            g_link = element.find("a").get('href')
            g_type = element2.find("p", {"class": "product__pangvContent"}).text
            g_uprice = element2.find("div", {"class": "unit-price"}).text
            if not element2.find("span", {"class": "reduced-price"}):
                g_rprice = ''
                g_price = element2.find("div", {"class": "price"}).text
            else:
                g_rprice = element2.find("span", {"class": "reduced-price"}).text
                g_price = element2.find("span", {"class": "instead-price"}).text
            
            g_exist = '1' if not element2.find('p', class_='stockstate state-red') else '0'
            
            if not element.find('a', class_='productVariants'):
                    g_variants = '0'
            else:
                n = element.find('a', class_='productVariants').text
                g_variants = '0' if n[-2:] == ' g' else '1'

            g_name_clean = g_name.replace('\u200b', '').strip()
            g_link = 'https://www.3djake.com' + g_link.strip()


            if g_exist == '1' and g_variants == '1':
                variants = load_good(g_link)
                for g_full in variants:
                    g_link = g_full[1]
                    g_type = g_full[2]
                    g_uprice = g_full[3]
                    g_price = g_full[4]
                    g_rprice = g_full[5]
                    g_exist = g_full[6]
                    filrow.append(g_name_clean)
                    filrow.append(g_link)
                    filrow.append(g_type)
                    filrow.append(g_uprice)
                    filrow.append(g_price)
                    filrow.append(g_rprice)
                    filrow.append(g_exist)
                    filrow.append(g_variants)
                    with open(fname, "a", newline="") as file:
                                writer = csv.writer(file)
                                writer.writerow(filrow)
                    filrow = []
                    
                    

            else:

                filrow.append(g_name_clean)
                filrow.append(g_link)
                filrow.append(g_type)
                filrow.append(g_uprice)
                filrow.append(g_price)
                filrow.append(g_rprice)
                filrow.append(g_exist)
                filrow.append(g_variants)

                with open(fname, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(filrow)
                filrow = []
    
    except requests.exceptions.ConnectionError:
        with open(fname, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(url)
        pass                         
   

def load_good(l):
    try:
        url = l
        html = urllib.request.urlopen(url, timeout=100)
        browser = webdriver.Firefox()
        browser.get(url)
        browser.refresh()
        x = browser.current_window_handle
        #browser.execute_script("window.onblur = function() { window.onfocus() }") 
        browser.switch_to.window(x)
        source_data = browser.page_source
        soup = BeautifulSoup(source_data,features="html5lib")
        list_goods = soup.find_all("ul", {"class": "p-variants__list"})
        vars_url = []
        element = list_goods[0].find_all("li", {"class": "p-variants__item"})
        for i in element:
            var_id = i.find("input").get("value")
            var_url = url + "?sai=" + var_id
            vars_url.append(var_url)

        vars_data = []

        for urls in vars_url:
            browser.get(urls)
            browser.refresh()
            #browser.execute_script("window.onblur = function() { window.onfocus() }") 
            browser.switch_to.window(x)
            source_data = browser.page_source
            soup = BeautifulSoup(source_data,features="html5lib")
            g_url = urls
            g_type = soup.find("span", {"class": "p-variants__selected__content"}).text
            price_info = soup.find_all("div", {"class": "p-price"})
            for info in price_info:
                price_block = info.find("p", {"class": "p-price__main"})
                if not price_block.find("span", {"class": "p-price__reduced"}):
                    g_rprice = ''
                    g_price = price_block.find("span", {"class": "p-price__retail"}).text
                else:
                    g_rprice = price_block.find("span", {"class": "p-price__reduced"}).text
                    g_price = price_block.find("span", {"class": "p-price__instead"}).text
                
                if not info.find("span", {"class": "p-price__perunit"}):
                    g_uprice = "?"
                else:
                    g_uprice = info.find("span", {"class": "p-price__perunit"}).text
            stock_info = soup.find_all("div", {"class": "p-delivery"})
            g_stock = stock_info[0].find("p",{"class": "p-delivery__stock"}).text.strip()
            if g_stock[:13] == 'Not available':
                clean_g_stock = 'Not available'
            else:
                form = soup.find_all("div", {"class": "p-main"})
                g_form = form[0].find("form", {"class": "p-buyform"})
                r = g_form.find("p", {"class": "p-stock"}).get("data-limit")
                clean_g_stock = g_stock + ' ' + r

            clean_uprice = g_uprice.replace('\xa0', ' ').strip()
            clean_g_price = g_price.replace('\xa0', ' ').strip()
            clean_g_rprice = g_rprice.replace('\xa0', ' ').strip()
            
            browser.execute_script("window.onblur = function() { window.onfocus() }") 

            varrow = []
            varrow.append(url)
            varrow.append(g_url)
            varrow.append(g_type)
            varrow.append(clean_uprice)
            varrow.append(clean_g_price)
            varrow.append(clean_g_rprice)
            varrow.append(clean_g_stock)

            vars_data.append(varrow)

        browser.close()

        return vars_data
            #with open(fname, "a", newline="") as file:
            #    writer = csv.writer(file)
            #    writer.writerow(varrow)
            #varrow = []
    except requests.exceptions.ConnectionError:
        fname = r'files/' + '3dbase' + '.csv'
        with open(fname, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(url)
        pass            


for i in range(1, 86):
    #add 1 more for final page
    load_base(i)
    print(i)
    t = random.uniform(5,15)
    time.sleep(t)
import json
import os
import time
from datetime import datetime, timedelta

import django
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caracol.settings')

django.setup()

from main import models
from selenium.webdriver import FirefoxOptions


def start(request):
    search()
    searchMarina()
    sender()
    return HttpResponse('completo')


def search():
    path = 'https://www.tiendascaracol.com/products/search'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/72.0.3626.119 Safari/537.36 "
    }
    options = Options()
    # options.binary_location = '/usr/bin/fire'
    # firefox_binary = FirefoxBinary('/usr/bin/firefox-esr')
    # opts = FirefoxOptions()
    # opts.add_argument('--headless')
    driver = webdriver.Chrome()
    driver.get(path)
    data = '{"municipality": "null", "province": {"id": 3, "name": "La Habana"}, "business": "null"}'
    driver.execute_script(f"localStorage.setItem('location',{json.dumps(data)})")
    driver.refresh()
    time.sleep(5)

    try:
        elem = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/footer/button[3]")
        elem.send_keys(Keys.ENTER)
    except:
        pass
    for i in range(2):
        try:
            elem = driver.find_element(By.XPATH, "/html/body/app-root/div/app-main/mat-sidenav-container/mat-sidenav"
                                                 "-content/app-product-left-sidebar/div/div[2]/div[2]/div[2]/div["
                                                 "2]/button")
            elem.send_keys(Keys.ENTER)
            time.sleep(5)
        except:
            pass

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lista = soup.find_all("app-product")
    for x in lista:
        producto = x.find(attrs={'class': 'card-product'}).find(attrs={'class': 'title'})
        precio = x.find(attrs={'class': 'price-offer'}).text
        tienda = 'caracol'
        try:
            name = producto.text
        except:
            pass
        else:
            obj, created = models.Producto.objects.get_or_create(name=name, precio=precio, tienda=tienda)
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

    driver.close()

    return True


def searchMarina():
    path = 'https://tienda.marinasmarlin.com/products/search'
    driver = webdriver.Firefox()
    driver.get(path)
    data = '{"municipality": "null", "province": {"id": 3, "name": "La Habana"}, "business": "null"}'
    driver.execute_script(f"localStorage.setItem('location',{json.dumps(data)})")
    driver.refresh()
    time.sleep(5)

    try:
        elem = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/footer/button[3]")
        elem.send_keys(Keys.ENTER)
    except:
        pass
    for i in range(2):
        try:
            elem = driver.find_element(By.XPATH, "/html/body/app-root/div/app-main/mat-sidenav-container/mat-sidenav"
                                                 "-content/app-product-left-sidebar/div/div[2]/div[2]/div[2]/div["
                                                 "2]/button")
            elem.send_keys(Keys.ENTER)
            time.sleep(5)
        except:
            pass

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lista = soup.find_all("app-product")
    for x in lista:
        producto = x.find(attrs={'class': 'card-product'}).find(attrs={'class': 'title'})
        precio = x.find(attrs={'class': 'price-offer'}).text
        tienda = 'Marina'
        try:
            name = producto.text
        except:
            pass
        else:
            obj, created = models.Producto.objects.get_or_create(name=name, precio=precio, tienda=tienda)
            if not created:
                obj.updated_at = timezone.now()
                obj.save()

    driver.close()

    return True


def sendTelegram(message):
    bot_key = "5826956567:AAH4wO2YWbvg3pbZVQ2PHvksBc38fj81B7E"
    chat = "-859697075"
    url = f'https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={message}&parse_mode=markdown'
    response = requests.get(url)
    print(response)


def sender():
    five_minutes = timezone.now() - timezone.timedelta(minutes=15)
    non_sended = models.Producto.objects.filter(updated_at__isnull=True)
    print(f'hay {len(non_sended)} productos')
    for prod in non_sended:
        sendTelegram(f'{prod.tienda}: {prod.precio} - {prod.name}')
        prod.sended = True
        prod.updated_at = timezone.now()
        prod.save()
        time.sleep(1)
    models.Producto.objects.filter(updated_at__lt=five_minutes).delete()

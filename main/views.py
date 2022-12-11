import json
import os
import time

import django
import requests
from bs4 import BeautifulSoup
from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caracol.settings')

django.setup()

from main import models


def start(request):
    search()
    return HttpResponse('completo')


def search():
    path = 'https://www.tiendascaracol.com/products/search'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/72.0.3626.119 Safari/537.36 "
    }
    driver = webdriver.Firefox()
    driver.get(path)
    data = '{"municipality": "null", "province": {"id": 3, "name": "La Habana"}, "business": "null"}'
    driver.execute_script(f"localStorage.setItem('location',{json.dumps(data)})")
    driver.refresh()
    time.sleep(5)
    elem = driver.find_element(By.CLASS_NAME, "accept-button")
    elem.send_keys(Keys.ENTER)
    for i in range(5):
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
    print(len(lista))
    for x in lista:
        producto = x.find(attrs={'class': 'card-product'}).find(attrs={'class': 'title'})
        try:
            name = producto.text
        except:
            pass
        else:
            obj = models.Producto.objects.get_or_create(name=name)

    return True


def sendTelegram(message):
    bot_key = "5826956567:AAH4wO2YWbvg3pbZVQ2PHvksBc38fj81B7E"
    chat = "-859697075"
    url = f'https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={message}&parse_mode=markdown'
    response = requests.get(url)
    print(response)


def sender(request):
    non_sended = models.Producto.objects.filter(sended=False)
    for prod in non_sended:
        sendTelegram(prod.name)
        prod.sended = True
        prod.save()
        time.sleep(1)

import datetime
import json
import os
import time

import django
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caracol.settings')

django.setup()

from main import models


def start(request):
    # now = datetime.datetime.now()
    # if now.minute == 0 and now.hour % 3 == 0 and now.hour in range(8, 20):
    #     sendTelegram("El bot está trabajando normalmente v1 ")
    #     time.sleep(1)
    # if now.hour == 8 and now.minute == 0:
    #     sendTelegram("Recapitulando todos los productos existentes")
    #     time.sleep(2)
    #     models.Producto.objects.all().delete()
    #     sender()
    search()
    sender()
    print(f'hay {models.Producto.objects.count()} productos')

    return HttpResponse(f'hay {models.Producto.objects.count()} productos')


def search():
    paths = ['https://www.tiendascaracol.com/products/search', 'https://tienda.marinasmarlin.com/products/search']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/72.0.3626.119 Safari/537.36 "
    }
    # driver_location = '/usr/bin/chromedriver'
    # binary_location = '/usr/bin/google-chrome'

    options = webdriver.FirefoxOptions()
    # options.binary_location = binary_location
    # options.add_argument('--no-sandbox')
    # options.add_argument('--headless')

    driver = webdriver.Firefox()
    # driver = webdriver.Chrome(executable_path=driver_location, options=options)
    for path in paths:
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
        for i in range(1, 20):
            try:
                if 'marina' in path:
                    tienda = 'marina'
                else:
                    tienda = 'caracol'
                searchitems(driver, tienda)
                elem = driver.find_element(By.XPATH,
                                           f'/html/body/app-root/div/app-main/mat-sidenav-container/mat-sidenav'
                                           '-content/app-product-left-sidebar/div/div[2]/div[2]/div[2]/div['
                                           f'2]/guachos-simple-pagination/nav/ul/li[{i + 1}]/a')
                elem.send_keys(Keys.ENTER)
            except:
                pass

    driver.close()

    return True


def searchitems(driver, tienda):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lista = soup.find_all("app-product")
    for x in lista:
        producto = x.find(attrs={'class': 'card-product'}).find(attrs={'class': 'title'})
        precio = x.find(attrs={'class': 'price-offer'}).text
        try:
            name = producto.text
        except:
            pass
        else:
            obj, created = models.Producto.objects.get_or_create(name=name, precio=precio, tienda=tienda)
            if not created:
                obj.updated_at = timezone.now()
                obj.save()


def sendTelegram(message, parse_mode='markdown'):
    bot_key = "1201814283:AAH-yjQapWH60uVogImL4OXj86CKLsneJWc"
    chat = "-4029790020"
    for char in ['_', '&']:
        if char in message:
            message = message.replace(char, '')
    url = f'https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={message}&parse_mode={parse_mode}'
    response = requests.get(url)
    print(response.json())

    # return response.status_code


def sender():
    non_sended = models.Producto.objects.filter(
        Q(updated_at__isnull=True) | Q(last_send__isnull=True))
    for prod in non_sended:
        status = sendTelegram(f'*{prod.tienda}*: {prod.precio} - {prod.name}')
        print(f'*{prod.tienda}*: {prod.precio} - {prod.name}')
        if status < 400:
            prod.sended = True
            prod.updated_at = timezone.now()
            prod.last_send = timezone.now()
            prod.save()
        time.sleep(1)

    five_minutes = timezone.now() - timezone.timedelta(minutes=60)
    old = models.Producto.objects.filter(updated_at__lt=five_minutes)
    if old.count() > 0:
        message = "Los siguiente productos se agotaron. Procediendo a eliminarlos: "
        for prod in old:
            message += f'*{prod.tienda}*: {prod.precio} - {prod.name}, '
            prod.delete()
        sendTelegram(message)


def revolico():
    path = 'https://www.revolico.com/search?order=relevance&category=vivienda&subcategory=compra-venta&province=la-habana'
    # driver_location = '/usr/bin/chromedriver'
    # binary_location = '/usr/bin/google-chrome'

    # options = webdriver.FirefoxOptions()
    # options.binary_location = binary_location
    # options.add_argument('--no-sandbox')
    # options.add_argument('--headless')

    driver = webdriver.Firefox()
    # driver = webdriver.Chrome(executable_path=driver_location, options=options)
    driver.get(path)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lista = soup.find_all(attrs={"data-cy": "adGrid"})
    for link in lista:
        link_real = link.find('a')
        subPage(link_real.get('href'))

    # for i in lista:
    #     print(i.text)
    # sendTelegram(i.text)
    driver.close()

    return True


def subPage(path):
    driver = webdriver.Firefox()
    path = f'https://www.revolico.com{path}'
    driver.get(path)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lista = soup.find_all(attrs={"data-cy": "adDescription"})
    contacts = soup.find_all(attrs={"class": "bzaqyz"})
    price = soup.find(attrs={"data-cy": "adPrice"})
    location = soup.find(attrs={"data-cy": "adLocation"})
    for item in lista:
        parrafo = item.find('p')
        message = f'{path}  \n'
        if price:
            message += f'Precio: {price.text}  \n'
        if location:
            message += f'Lugar: {location.text}  \n'
        contacts_text = ''
        for phone in contacts:
            contacts_text += phone.get('href')
        if len(contacts_text) > 0:
            message += f'Contactos: {contacts_text}  \n'
        message += f'Anuncio: {parrafo.text}'
        print(message)
        sendTelegram(message, 'html')
    driver.close()
    return True

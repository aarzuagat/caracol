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
    searchCaracol()
    searchMarina()
    sender()
    print(f'hay {models.Producto.objects.count()} productos')

    return HttpResponse(f'hay {models.Producto.objects.count()} productos')


def searchCaracol():
    paths = ['https://www.tiendascaracol.com/products/search']

    driver_location = '/usr/bin/chromedriver'
    binary_location = '/usr/bin/google-chrome'

    options = webdriver.ChromeOptions()
    # options = webdriver.FirefoxOptions()
    options.binary_location = binary_location
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')

    # driver = webdriver.Firefox()
    driver = webdriver.Chrome(executable_path=driver_location, options=options)
    for key, path in enumerate(paths):
        driver.get(path)
        data = '{"municipality": "null", "province": {"id": 3, "name": "La Habana"}, "business": "null"}'
        driver.execute_script(f"localStorage.setItem('location',{json.dumps(data)})")
        driver.refresh()
        time.sleep(5)
        tienda = 'caracol'
        try:
            elem = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/footer/button[3]")
            elem.send_keys(Keys.ENTER)
        except:
            pass
        for i in range(1, 20):
            try:
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
def searchMarina():
    paths = ['https://tienda.marinasmarlin.com/products/search']
    driver_location = '/usr/bin/chromedriver'
    binary_location = '/usr/bin/google-chrome'

    options = webdriver.ChromeOptions()
    # options = webdriver.FirefoxOptions()
    options.binary_location = binary_location
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # driver = webdriver.Firefox()
    driver = webdriver.Chrome(executable_path=driver_location, options=options)
    for key, path in enumerate(paths):
        driver.get(path)
        data = '{"municipality": "null", "province": {"id": 3, "name": "La Habana"}, "business": "null"}'
        driver.execute_script(f"localStorage.setItem('location',{json.dumps(data)})")
        driver.refresh()
        time.sleep(5)
        tienda = 'marina'

        try:
            elem = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/footer/button[3]")
            elem.send_keys(Keys.ENTER)
        except:
            pass
        for i in range(1, 20):
            try:
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
    return True


def sendTelegram(message):
    bot_key = "5826956567:AAH4wO2YWbvg3pbZVQ2PHvksBc38fj81B7E"
    chat = "-1001802874612"
    for char in ['_', '&']:
        if char in message:
            message = message.replace(char, '')
    url = f'https://api.telegram.org/bot{bot_key}/sendMessage?chat_id={chat}&text={message}&parse_mode=markdown'
    response = requests.get(url)
    print(response.text)
    return response.status_code


def sender():
    non_sended = models.Producto.objects.filter(
        Q(updated_at__isnull=True) | Q(last_send__isnull=True))
    for prod in non_sended:
        status = sendTelegram(f'*{prod.tienda}*: {prod.precio} - {prod.name}')
        print(f"el status es {status}")
        if status < 400:
            prod.sended = True
            prod.updated_at = timezone.now()
            prod.last_send = timezone.now()
            prod.save()
        time.sleep(2)

    five_minutes = timezone.now() - timezone.timedelta(minutes=60)
    old = models.Producto.objects.filter(updated_at__lt=five_minutes)
    if old.count() > 0:
        message = "Los siguiente productos se agotaron. Procediendo a eliminarlos: "
        for prod in old:
            message += f'*{prod.tienda}*: {prod.precio} - {prod.name}, '
            prod.delete()
        sendTelegram(message)

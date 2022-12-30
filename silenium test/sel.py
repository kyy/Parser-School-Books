from bs4 import BeautifulSoup
from pathlib import Path
import requests
import urllib.request
import shutil
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def start_browser():
    res = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        #options.add_argument('headless')  # закомментируй, если хочется видеть браузер
        options.add_argument('--verbose')
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.set_page_load_timeout(60)
        res = driver
    except:
        pass
    return res


def get_brands():       # парсим все бренды авто и записывем в файл 'brands.txt'
    driver = start_browser()

    driver.get("https://cars.av.by/")

    time.sleep(5)
    brands_all_show = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[2]/div[2]/p/button').click()     # раскрываем списко всех брендов авто
    time.sleep(1)
    brands = driver.find_elements(By.CLASS_NAME, 'catalog__title')      # находим все имена брендов
    brands_list = []

    try:
        for brand in brands:
            name = brand.text   # извлекаем имена брендов
            brands_list.append(name)    # добавляем в пустой список
        brands_list.sort()      # сортируем спискок
        print('OK--парсинг брендов')
    except Exception as e:
        print('ERROR--парсинг брендов', e)

    try:
        for brand in brands_list:
            with open("brands.txt", "a") as file:
                file.write(f"\n{brand}")    # записываем в файл все бренды построчно
                file.close()
        print('OK--запись файл')
    except Exception as e:
        print('ERROR--запись файл', e)

get_cars_input = 'audi a7 d a 1990 2022 3000 35000 1600 3000'

def car_parturl():       # парсим все бренды авто и записывем в файл 'brands.txt'

    list_param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=', 'year[max]=', 'price_usd[min]=', 'price_usd[max]=',
                        'engine_capacity[min]', 'engine_capacity[max]']
    car_input = dict(zip(list_param_input, get_cars_input.split(' ')))
    transmission = {'a': '1', 'm': '2'}
    motor = {'b': '1', 'bpb': '2', 'bm': '3', 'bg': '4', 'd': '5', 'dg': '6', 'e': '7'}

    if car_input['transmission_type='] == 'a':
        car_input['transmission_type='] = '1'
    else:
        car_input['transmission_type='] = '2'

    for key in motor:
        if key == car_input['engine_type[0]=']:
            car_input['engine_type[0]='] = motor[key]

    new_part = []
    for key in car_input:
        if car_input[key] != '-':
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part[2:])

    driver = start_browser()
    driver.get(f"https://cars.av.by/{car_input['brands[0][brand]=']}/{car_input['brands[0][model]=']}")
    time.sleep(5)
    cost_1 = driver.find_element(By.XPATH, '//*[@id="p-9-price_usd"]').send_keys('1')     # устанавливаем минимальную цену - '1' - для получения url
    time.sleep(0.5)
    click_show = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[3]/form/div/div[3]/div/div[3]/div[2]/div[2]/button/span').click()     # жмем кнопу фильтра
    time.sleep(0.5)
    link = driver.current_url       # получаем ссылку с ввода в браузер
    current_car = '&'.join(link.replace('https://cars.av.by/filter?', '').split('&')[0:2])      # чистим ссылку и получаем get-запроc на нашу машину

    time.sleep(0.5)
    driver.get(f"https://cars.av.by/filter?{current_car}"+f"&{new_part_url}")
    print(f"https://cars.av.by/filter?{current_car}"+f"&{new_part_url}")
    time.sleep(100)

if __name__ == '__main__':
    car_parturl()




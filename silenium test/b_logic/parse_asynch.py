import asyncio
import numpy as np
from aiohttp import ClientSession
import requests
from multiprocessing import Pool
from time import sleep
from bs4 import BeautifulSoup
import time
import nest_asyncio


nest_asyncio.apply()

stoptask = 'https://www.cyberforum.ru/python-beginners/thread3009742.html'
source = 'https://habr.com/ru/post/319966/'
root = 'https://av.by/'
url = 'https://cars.av.by/rover'


def get_pages(url):
    """
    парсим ссылки на машины
    :param url: ссылка на страницу результата поиска
    :return: спимок ссылок на машины
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103.0.0.0 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(url, headers=headers)
    r = r.content
    html = BeautifulSoup(r, "lxml", )
    link_list = []
    try:
        link = html.select('.listing-item__link')
        for lin in link:
            link = lin.get('href')
            link_list.append('https://cars.av.by' + link)
    except:
        pass
    return link_list


# def main():
#     # Загружаем ссылки на страницы жанров из нашего .json файла.
#     dict = json.load(open('genres.json', 'r'))
#     p = Pool(4)
#     # Простой пул. Функцией map отдаем каждому потоку его порцию жанров для парсинга.
#     p.map(get_pages, [dict[key] for key in dict.keys()])
#     print('Over')
#
# if __name__ == "__main__":
#     main()


def parsing_car_pages(html, url):
    """
    парсим описание машин
    :param html: тело ссылки на машину
    :param url: ссылка на машину
    :return: список параметров машины
    """
    try:
        html = BeautifulSoup(html, "lxml", )
    except Exception as e:
        print(e, f'\n Ошибка при получении контента страницы - {url}')
        sleep(1)
        return parsing_car_pages(html, url)
    try:
        info_param = html.find('div', class_='card__params').text.split(', ')
        year = info_param[0].strip()[0:5]
        transmission = info_param[1]
        dimension = info_param[2].strip().replace('электро', 'эл.')
        motor = info_param[3]
        km = info_param[4].strip()
    except Exception as e:
        print(e, f'\n Ошибка при получении info_param - {url}')
        year = '-'
        transmission = '-'
        dimension = '-'
        motor = '-'
        km = '-'
    try:
        info_description = html.find('div', class_='card__description').text.split(', ')
        type = info_description[0].strip()
        drive = info_description[1].strip().replace('привод', '').replace('постоянный', 'пост.')
        color = info_description[2].strip()
    except Exception as e:
        print(e, f'\n Ошибка при получении info_description - {url}')
        type = ''
        drive = ''
        color = ''
    try:
        cost = html.find('div', class_='card__price-secondary').getText('span')[0].strip().replace('≈ ', '')
    except Exception as e:
        print(e, f'\n Ошибка при получении цены - {url}')
        cost = ''
    try:
        model = html.find('h1', class_='card__title').text.split(', ')[0][8:].replace('Рестайлинг', 'Рест.')
    except Exception as e:
        print(e, f'\n Ошибка при получении модели - {url}')
        model = ''
    try:
        data = html.find_all('li', class_='card__stat-item')[1].text.replace('опубликовано', 'опубл.').replace('обновлено', 'обн.')
    except Exception as e:
        print(e, f'\n Ошибка при получении даты - {url}')
        data = ''
    try:
        comment = html.find('div', class_='card__comment-text').text.strip().replace('• ', ' ')
    except Exception as e:
        print(e, f'\n Ошибка при получении комментария- {url}')
        comment = ''
    try:
        exchange = html.find('h4', class_='card__exchange-title').text.casefold().replace('обмен ', '')
    except Exception as e:
        print(e, f'\n Ошибка при получении обмена - {url}')
        exchange = ''
    try:
        vin = html.find('div', class_='badge badge--vin').text
    except AttributeError as e:
        print(f'\n vin не указан - {url}')
        vin = ''
    try:
        city = html.find('div', class_='card__location').text.split(', ')[0]
    except Exception as e:
        print(e, f'\n Ошибка при получении города - {url}')
        city = ''

    #print(f'{year}\n{transmission}\n{dimension}\n{motor}\n{km}\ncost: {cost}\nmodel: {model}\ndata: {data}\ncomment:{comment}\ncity: {city}\nexcjange: {exchange}\nvin: {vin}\ntype: {type}\ndrive: {drive}\ncolor: {color}')
    return [url, comment, model, cost, motor, dimension, transmission, km,
            year, type, drive, color, vin, exchange, data, city]


async def bound_fetch(semaphore, url, session, result):
    try:
        async with semaphore:
            await get_one(url, session, result)
    except Exception as e:
        print(e)
        # Блокируем все таски на <> секунд в случае ошибки 429.
        sleep(0.05)



async def get_one(url, session, result):
    async with session.get(url) as response:
        page_content = await response.read()    # Ожидаем ответа и блокируем таск.
        item = parsing_car_pages(page_content, url)      # Получаем информацию об машине и сохраняем в лист.
        result.append(item)
        print(url)


async def run(urls, result):
    tasks = []
    # Выбрал лок от балды. Можете поиграться.
    semaphore = asyncio.Semaphore(5)
    headers = {"User-Agent": "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"}
    # Опять же оставляем User-Agent, чтобы не получить ошибку от Metacritic
    async with ClientSession(
            headers=headers) as session:
        for url in urls:
            # Собираем таски и добавляем в лист для дальнейшего ожидания.
            task = asyncio.ensure_future(bound_fetch(semaphore, url, session, result))
            tasks.append(task)
        # Ожидаем завершения всех наших задач.
        await asyncio.gather(*tasks)


def main(url):
    result = []
    # Запускаем наш парсер.
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(get_pages(url), result))
    loop.run_until_complete(future)
    np.save(f'parse_av_by.npy', result)
    print('ok')
    return result


if __name__ == "__main__":
    main(url)
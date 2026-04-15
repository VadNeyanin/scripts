import requests
import json
from bs4 import BeautifulSoup
import telebot
from datetime import datetime, timedelta
import locale
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
import os

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
today = datetime.now()
week_ago = today - timedelta(days=7)
print(week_ago)
url_astra = 'https://astra.ru/about/press-center/news'
url_rosa = 'https://rosa.ru/news/'
url_alt = 'https://www.basealt.ru/about/news'
url_redos = 'https://redos.red-soft.ru/about/news/novosti/'
url_mtslink = 'https://mts-link.ru/blog/category/news/'
print('-----------------------------------------------')
bot = telebot.TeleBot('')

#--------------------------------------------------------------------------------------------------------

def is_date_too_old(date_obj):
    """Проверяет, прошло ли более 7 дней с даты"""
    today = datetime.now().date()
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    print((today - date_obj).days)
    return (today - date_obj).days > 15

#--------------------------------------------------------------------------------------------------------

#def mess(name, link, date, summary):
#    chat_id = '-1002053802286'
#    message = f'''<b>{name}</b>

#{summary}

#Дата публикации: {date}

#<a href="{link}">Читать полностью</a>'''
#    bot.send_message(chat_id, message, message_thread_id=133, parse_mode='HTML')

#--------------------------------------------------------------------------------------------------------
news_list = []
def mess(name, link, date, summary):
    news_list.append({
        'name': name,
        'link': link,
        'date': date,
        'summary': summary
    })

def create_docx_file(filename=None):
    if not news_list:
        print("Нет новостей для сохранения")
        return None
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"news_{timestamp}.docx"
    
    document = Document()
    
    title = document.add_heading('Сводка новостей', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    date_paragraph = document.add_paragraph()
    date_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    date_paragraph.add_run(f"Дата формирования: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    
    document.add_paragraph()
    
    for idx, news in enumerate(news_list, 1):
        heading = document.add_heading(f"{idx}. {news['name']}", level=1)
        summary_para = document.add_paragraph()
        summary_run = summary_para.add_run(news['summary'])
        summary_run.font.size = Pt(12)
        
        date_para = document.add_paragraph()
        date_run = date_para.add_run(f"Дата публикации: {news['date']}")
        date_run.font.size = Pt(10)
        date_run.italic = True
        
        link_para = document.add_paragraph()
        link_run = link_para.add_run(f"Ссылка: {news['link']}")
        link_run.font.size = Pt(10)
        
        document.add_paragraph('─' * 50)
    
    document.save(filename)
    print(f"Документ сохранен: {filename}")
    
    
    return filename
    

#--------------------------------------------------------------------------------------------------------

def ollama(name, context):
    prompt = f'''
    Ты - редактор новостей об импортозамещении в IT в России. Ты получил контекст новости и заголовок. На его основе создай краткое summary в 2-4 предложения, которое отразит основную идею и смысл новости.
        
    Заголовок: {name}
    
    Контекст новости: {context}
    '''
    
    response = requests.post('http://10.194.2.203:11434/api/generate', 
        json={
            'model': 'gemma3:12b',
            'prompt': prompt,
            'stream': False
        }
    )
    return response.json()['response']

#--------------------------------------------------------------------------------------------------------

def astra(url_astra):
    page = requests.get(url_astra)
    soup = BeautifulSoup(page.text, "html.parser")
    news = soup.find_all('div', class_='news__item news__item--sm col-12 col-md-6 col-xl-4')
    for i in news:
        title = i.find('a', class_='news__item-title')
        name = title.text.strip()
        link = f"https://astra.ru{title.get('href')}"
        date_from_page = i.find('span', class_="briefly briefly--tiny briefly--date").text.strip()
        date_in_format = datetime.strptime(date_from_page, '%d %B %Y')
        if is_date_too_old(date_in_format):
            break
        date = date_in_format.strftime('%d.%m.%Y')
        news_page = requests.get(link)
        news_soup = BeautifulSoup(news_page.text, "html.parser")
        news_context = news_soup.find('div', class_='article__content-txt').text.strip()
        summary = ollama(name, news_context)
        print('Новость: ', name)
        print('Ссылка: ', link)
        print('Дата новости: ', date)
        print('Содержание: ', news_context)
        print('Ответ:', summary)
        print('-----------------------------------------------')
        send = mess(name, link, date, summary)
res = astra(url_astra)

#--------------------------------------------------------------------------------------------------------

def rosa(url_rosa):
    page = requests.get(url_rosa)
    soup = BeautifulSoup(page.text, "html.parser")
    news = soup.find('div', id='recent-posts-2')
    news = news.find('ul').find_all('li')
    for i in news:
        link_tag = i.find('a')
        name = link_tag.get_text(strip=True)
        link = link_tag.get('href')
        news_page = requests.get(link)
        news_soup = BeautifulSoup(news_page.text, "html.parser")
        date_element = soup.find('li', class_='meta-date')
        if not date_element:
            date_element = news_soup.find(attrs={"itemprop": "datePublished"})
        if date_element:
            full_text = date_element.get_text(strip=True)
            date = full_text.replace('Запись опубликована:', '').strip()
        else:
            date = "Дата не найдена"
        date_in_format = datetime.strptime(date, "%d.%m.%Y")
        if is_date_too_old(date_in_format):
            break
        news_context = news_soup.find('div', class_='entry-content')
        news_context = news_context.get_text()
        summary = ollama(name, news_context)
        print('Новость:', name)
        print('Ссылка:', link)
        print('Дата новости:', date)
        print('Содержание:', news_context)
        print('Ответ:', summary)
        print('-----------------------------------------------')
        send = mess(name, link, date, summary)
res = rosa(url_rosa)

#--------------------------------------------------------------------------------------------------------

def alt(url_alt):
    page = requests.get(url_alt)
    soup = BeautifulSoup(page.text, "html.parser")
    news = soup.find_all('div', class_='news_item')
    for title in news:
        name = title.find('a', class_='head').text.strip()
        link = title.find('a', class_='head')['href']
        if "https" not in link:
            link = f"https://www.basealt.ru{link}"
        date_from_page = title.find('div', class_="date").text.strip()
        date_in_format = datetime.strptime(date_from_page, '%d %B %Y')
        if is_date_too_old(date_in_format):
            break
        date = date_in_format.strftime('%d.%m.%Y')
        news_page = requests.get(link)
        news_soup = BeautifulSoup(news_page.text, "html.parser")
        articles = news_soup.find_all(['article', 'h2'])
        #news_context = news_soup.find('article', class_='flex-item_1').text.strip()
        news_context = news_soup.get_text(separator=' ', strip=True)
        summary = ollama(name, news_context)
        print('Новость: ', name)
        print('Ссылка: ', link)
        print('Дата новости: ', date)
        print('Содержание: ', news_context)
        print('Ответ:', summary)
        print('-----------------------------------------------')
        send = mess(name, link, date, summary)
res = alt(url_alt)

#--------------------------------------------------------------------------------------------------------

def redos(url_redos):
    page = requests.get(url_redos)
    soup = BeautifulSoup(page.text, "html.parser")
    news = soup.find_all('div', class_='news-list__item')
    for i in news:
        title = i.find('img')
        name = title['alt']
        link_tag = i.find('a', href=True)
        link = f"https://redos.red-soft.ru{link_tag['href']}"
        date_div = i.find('div', class_="news__date")
        date_from_page = date_div.find('span').text.strip()
        date_in_format = datetime.strptime(date_from_page, '%d %B %Y')
        if is_date_too_old(date_in_format):
            break
        date = date_in_format.strftime('%d.%m.%Y')
        news_page = requests.get(link)
        news_soup = BeautifulSoup(news_page.text, "html.parser")
        news_context = news_soup.find('article', class_='news-article').text.strip()
        summary = ollama(name, news_context)
        print('Новость: ', name)
        print('Ссылка: ', link)
        print('Дата новости: ', date)
        print('Содержание: ', news_context)
        print('Ответ:', summary)
        print('-----------------------------------------------')
        send = mess(name, link, date, summary)
res = redos(url_redos)

#--------------------------------------------------------------------------------------------------------

def mtslink(url_mtslink):
    page = requests.get(url_mtslink)
    soup = BeautifulSoup(page.text, "html.parser")
    news = soup.find_all('a', class_='articles__item')
    for i in news:
        title = i.find('div', class_='articles__item-title')
        name = title.text.strip()
        link = i['href']
        bottom_section = i.select_one('.articles__item-bottom')
        date_from_page = bottom_section.select_one('.articles__item-text').text.strip()
        #date_from_page = i.find('div', class_='articles__item-title').text.strip()
        date_in_format = datetime.strptime(date_from_page, '%d %B %Y')
        if is_date_too_old(date_in_format):
            break
        date = date_in_format.strftime('%d.%m.%Y')
        news_page = requests.get(link)
        news_soup = BeautifulSoup(news_page.text, "html.parser")
        news_context = news_soup.find('div', class_='wrapper').get_text(strip=True, separator=' ')
        summary = ollama(name, news_context)
        print('Новость: ', name)
        print('Ссылка: ', link)
        print('Дата новости: ', date)
        print('Содержание: ', news_context)
        print('Ответ:', summary)
        print('-----------------------------------------------')
        send = mess(name, link, date, summary)
res = mtslink(url_mtslink)


create_docx_file("news.docx")

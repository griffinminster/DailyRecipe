import re
import urllib.request
import gspread
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials


def make_formula(url):
    formula = "=IMAGE(\"" + str(url) + "\")"
    return formula


def pad(inputs):
    return str(inputs) + "\n\n\n\n\n"


def cut_url(images):
    i = -1
    for j, pic in enumerate(images):
        if pic == ' ':
            i = j
            break
    return images[0:i]

def main():
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("venv/python-cookbook.json",
                                                                   scopes)
    file = gspread.authorize(credentials)
    worksheet = file.open("Daily Cookbook")
    worksheet = worksheet.sheet1


    nyt = 'https://cooking.nytimes.com/68861692-nyt-cooking/1640510-sam-siftons-suggestions'
    nyt_basic = 'https://cooking.nytimes.com'
    nyt_source = urllib.request.urlopen(nyt)
    nyt_soup = BeautifulSoup(nyt_source, 'lxml')

    ba = 'https://www.bonappetit.com/recipes'
    ba_basic = 'https://www.bonappetit.com/'
    ba_source = urllib.request.urlopen(ba)
    ba_soup = BeautifulSoup(ba_source, 'lxml')

    cooks = 'https://www.cooksillustrated.com/recipes'
    cooks_basic = 'https://www.cooksillustrated.com'
    cooks_source = urllib.request.urlopen(cooks)
    cooks_soup = BeautifulSoup(cooks_source, 'lxml')


    full_list = []

    for tag in nyt_soup.find_all(class_=re.compile("card recipe-card")):
        recipe_name = pad(tag.h3['data-name'])
        broken_url = nyt_basic + tag.a['href']
        full_url = pad(broken_url)
        image = make_formula(tag.img['src'])

        full_list.append([recipe_name, full_url, image])

    for tag in ba_soup.find_all(class_=re.compile("cards__li")):
        name = tag.find(class_=re.compile("card-body"))
        recipe_name = pad(name.h1.a.string)
        broken_url = ba_basic + tag.a['href']
        full_url = pad(broken_url)
        image = tag.source['srcset']
        image = make_formula(cut_url(image))

        full_list.append([recipe_name, full_url, image])

    for tag in cooks_soup.find_all(class_=re.compile("result recipe title-")):
        recipe_name = pad(tag.a['title'])
        broken_url = cooks_basic + tag.a['href']
        full_url = pad(broken_url)
        image = tag.img['src']
        image = make_formula(image)

        full_list.append([recipe_name, full_url, image])

    worksheet.update('A1', full_list)
    cell_list = worksheet.range('C1:C100')
    worksheet.update_cells(cell_list, value_input_option='USER_ENTERED')


if __name__ == '__main__':
    main()

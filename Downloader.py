import requests
from bs4 import BeautifulSoup
import pymorphy2


def parseRecipe(num: int):
    recipe = 'https://www.russianfood.com/recipes/recipe.php?rid={}'.format(num)
    page = requests.get(recipe)

    soup = BeautifulSoup(page.content, 'html.parser')
    recipe_place = soup.findAll('table', {'class': 'recipe_new'})[0]
    [s.extract() for s in recipe_place('script')]
    [s.extract() for s in recipe_place('style')]

    name = recipe_place.findAll('h1', {'class': 'title'})[0].text
    productsPlace = recipe_place.findAll('table', {'id': 'from'})[0]
    productNames = [norm(i.text.replace('\xa0', '')).replace('или','') for i in list(productsPlace.findAll('span', {'class': ''}))]
    productAmounts = [i[0].text.split('-')[-1] + ' ' + i[1].text for
                      i in zip(productsPlace.findAll('td', {'class': 'padding_l qnt'}),
                               productsPlace.findAll('td', {'class': 'padding_r'}))]
    # print(productsPlace.findAll('td', {'class': 'padding_r'})[1].text)
    products = list(zip(productNames, productAmounts))

    recipe = recipe_place.findAll('div', {'id': 'how'})[0].text.replace('\n', ' ').replace('. ', '.\n')
    recipe = '\n'.join([str(i + 1) + '. ' + j.strip() for i, j in enumerate(recipe.split('\n'))])

    # print(name, '\n--------')
    # print(products, '\n--------')
    # print(recipe)

    return (name, products, recipe)


def norm(x):
    morph = pymorphy2.MorphAnalyzer()
    p = morph.parse(x)[0]
    return p.normal_form


def toInitial():
    pass


def writeRecipe(i: int):
    try:
        recipe = parseRecipe(i)
        out = open('recipes/{}.recipe'.format(i), 'w', encoding='utf-8')
        out.write(recipe[0] + '\n')
        out.write('--------\n')

        for j in recipe[1]:
            out.write((j[0] + ' : ' + j[1]).replace('  ', ' ') + '\n')
        out.write('--------\n')

        out.write(recipe[2] + '\n')
        out.close()
        print('{})'.format(i), recipe[0], 'downloaded and saved successfully')
    except IndexError:
        print(i, ': No recipe with such index')


for i in range(1, 10):
    writeRecipe(i)

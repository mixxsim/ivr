import requests
from bs4 import BeautifulSoup
import pymorphy2
import os


def parseRecipe(num: int):
    recipe = 'https://www.russianfood.com/recipes/recipe.php?rid={}'.format(num)
    page = requests.get(recipe)

    soup = BeautifulSoup(page.content, 'html.parser')
    recipe_place = soup.findAll('table', {'class': 'recipe_new'})[0]
    [s.extract() for s in recipe_place('script')]
    [s.extract() for s in recipe_place('style')]

    name = recipe_place.findAll('h1', {'class': 'title'})[0].text
    productsPlace = recipe_place.findAll('table', {'id': 'from'})[0]
    productNames = [norm(i.text.replace('\xa0', '').replace('-', ':')).replace('или', '') for i in
                    list(productsPlace.findAll('span', {'class': ''}))]
    productNames = [i for i in productNames if i[0] != ':']

    recipe = [i.strip() + '\n' for i in recipe_place.findAll('table', {'class': 'step_images'})[0].text.split('\n') if
              i not in ['', ' ', '\r']]
    recipe = '\n'.join([f'{e+1}. ' + j for e, j in enumerate(recipe)])
    print(recipe)

    return (name, productNames, recipe)


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
            if (':' != j[-1] and j != '*'):
                out.write(j + '\n')
        out.write('--------\n')

        out.write(recipe[2])
        out.close()
        print('{}:'.format(i), recipe[0], 'downloaded and saved successfully')
    except IndexError as e:
        print(e)
        print(i, ': No recipe with such index')
        os.system(f"rm -rf recipes/{i}.recipe")



for i in range(147234, 147235):
    writeRecipe(i)

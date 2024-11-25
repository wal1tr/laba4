# myapp/views.py
import xml.etree.ElementTree as ET
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import RecipeForm
from .models import Recipe
from django.core.files.storage import default_storage
from django.http import HttpResponse
import os

def recipe_form(request):
    if request.method == "POST":
        form = RecipeForm(request.POST)
        if form.is_valid():
            # Сохраняем данные в БД
            recipe = form.save()

            # Сохраняем данные в XML
            recipe_xml = ET.Element("recipe")
            ET.SubElement(recipe_xml, "name").text = recipe.name
            ET.SubElement(recipe_xml, "ingredients").text = recipe.ingredients
            ET.SubElement(recipe_xml, "description").text = recipe.description
            tree = ET.ElementTree(recipe_xml)

            # Убедитесь, что директория для хранения рецептов существует
            recipes_dir = os.path.join(settings.MEDIA_ROOT, 'recipes')
            if not os.path.exists(recipes_dir):
                os.makedirs(recipes_dir)

            # Сохраняем XML файл
            tree.write(os.path.join(recipes_dir, f"{recipe.name}.xml"))

            return redirect('myapp:recipe_list')
    else:
        form = RecipeForm()

    return render(request, 'myapp/recipe_form.html', {'form': form})

def upload_file(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        
        # Убедитесь, что директория для загрузки существует
        recipes_dir = os.path.join(settings.MEDIA_ROOT, 'recipes')
        if not os.path.exists(recipes_dir):
            os.makedirs(recipes_dir)

        # Сохраните файл
        file_path = default_storage.save(f"recipes/{file.name}", file)
        file_ext = os.path.splitext(file.name)[1]

        # Проверяем валидность JSON/XML
        valid = False
        if file_ext == '.xml':  # Обратите внимание, что мы работаем только с XML
            try:
                ET.parse(file_path)  # Проверка валидности XML
                valid = True
            except ET.ParseError:
                pass

        if not valid:
            os.remove(file_path)
            return HttpResponse("Файл не валиден и был удален.")

        # Переадресовываем на список рецептов после успешной загрузки
        return redirect('myapp:recipe_list')

    return render(request, 'myapp/upload_file.html')


def recipe_list(request):
    # Список всех XML файлов
    recipes_dir = os.path.join(settings.MEDIA_ROOT, 'recipes')
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir)

    recipes = []  # Список для хранения уникальных рецептов
    seen_names = set()  # Множество для хранения имен, чтобы избежать дубликатов

    files = [f for f in os.listdir(recipes_dir) if f.endswith('.xml')]

    for file_name in files:
        file_path = os.path.join(recipes_dir, file_name)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            recipe = {child.tag: child.text for child in root}

            # Если рецепт успешно загружен и его имя уникально, добавим его в список
            if recipe['name'] not in seen_names:
                seen_names.add(recipe['name'])
                recipes.append(recipe)

        except ET.ParseError:
            continue  # Игнорируем файлы, которые не могут быть распознаны как XML

    return render(request, 'myapp/recipe_list.html', {'recipes': recipes})
def download_recipes_xml(request):
    recipes_dir = os.path.join(settings.MEDIA_ROOT, 'recipes')
    if not os.path.exists(recipes_dir):
        os.makedirs(recipes_dir)

    # Создаём корневой элемент
    root = ET.Element("recipes")

    # Считываем существующие рецепты и добавляем их в XML
    files = [f for f in os.listdir(recipes_dir) if f.endswith('.xml')]
    for file_name in files:
        file_path = os.path.join(recipes_dir, file_name)
        try:
            tree = ET.parse(file_path)
            recipe = tree.getroot()
            root.append(recipe)  # Добавляем рецепт в корневой элемент
        except ET.ParseError:
            continue  # Игнорируем файлы, которые не могут быть распознаны как XML

    # Генерируем ответ с заголовками для скачивания
    response = HttpResponse(ET.tostring(root, encoding='utf-8', method='xml'), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="recipes.xml"'
    return response
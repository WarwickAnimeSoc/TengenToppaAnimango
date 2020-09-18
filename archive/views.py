import re
from math import ceil

from django.shortcuts import render, get_object_or_404

from .models import Item


def index(request):
    # By default items are categorized by year
    items = Item.objects.all()

    years = set()
    for item_object in items:
        if item_object.date.year not in years:
            years.add(item_object.date.year)

    # We need to sort the years set now, otherwise it will be in the order that the items were added.
    years = sorted(years)

    year_data = []
    for year in years:
        year_data.append({'year': year, 'num_items': items.filter(date__year=year).count()})

    return render(request, 'archive/index.html', context={'years': year_data})


def year_view(request, year):
    # Display all the items for the given year. aniMango has items further split into months within a year, but this
    # wasn't really useful as the archive doesn't have more than 1 item per year.
    items = Item.objects.filter(date__year=year)
    return render(request, 'archive/year.html', context={'year': year, 'items': items})


def item_view(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    filesize = ceil(item.file.size / 1024)
    filename = re.sub(r'^(.*?)/', '', str(item.file.name))
    return render(request, 'archive/item.html', context={'item': item, 'filesize': filesize, 'filename': filename})


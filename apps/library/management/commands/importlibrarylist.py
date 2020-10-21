import time
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from apps.library.models import Item
from apps.showings.models import Series


def get_spreadsheet_data():
    # Load in the scope and the details of API credentials
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('apps/library/management/commands/authdetails.json',
                                                                   scope)
    client = gspread.authorize(credentials)

    # Select the right spreadsheet and the sheet that the data is on
    sheet = client.open("Library List Updated 2020").sheet1

    # Return the values that we need for later
    # [0] = Series title, [1] = Media type, [2] = Item volume number, [3] = Series anilist link, [4] = Extra details
    sheet_data = [sheet.col_values(1), sheet.col_values(2), sheet.col_values(3), sheet.col_values(4),
                  sheet.col_values(5)]
    return sheet_data


# Updates the spreadsheet at the specified position
def update_sheet(x, y, value):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('apps/library/management/commands/authdetails.json',
                                                                   scope)
    client = gspread.authorize(credentials)

    sheet = client.open("Library List Updated 2020").sheet1
    sheet.update_cell(y, x, value)


# This command was mostly taken from the library update command from the old aniMango site
# This command should only be needed once, which is to populate the library lists as it was at the time I created the
# library spreadsheet (Summer 2020) after the initial import series and items should be added
# thought the django admin
class Command(BaseCommand):
    help = 'Imports the library list from a google spreadsheet'

    def handle(self, *args, **options):
        sheet_data = get_spreadsheet_data()

        # The spreadsheet contains headers for each column in the first row, so indexing should start at 1 not 0
        for i in range(1, len(sheet_data[0])):
            # As the series title in the spreadsheet was entered by hand, it is preferable to use anilist to fetch the
            # title instead of using the spreadsheet value.
            series_title = sheet_data[0][i]
            # Not all series may have an anilist link, so sheet_data[3] may be shorter than len(sheet_data[0])
            try:
                series_anilist = sheet_data[3][i]
            except IndexError:
                series_anilist = None

            # Item fields
            # item_media_type should already be correctly formatted
            item_media_type = sheet_data[1][i]
            # Here we use the term volume_number to refer to the volume of the item. The Item model does  not contain a
            # field to store volume number, instead it has the name field.
            # For most items, the volume number on the spreadsheet matches the number of the real world volume. However,
            # certain DVD boxsets have been marked as 1 volume when they actually contain several smaller volumes within
            # them. For example, Planetes is listed as having 2 volumes, but these volumes are actually 2 boxsets which
            # contain 3 volumes each. The reason they are listed as 2 is that it it assumes someone will want to take
            # out the full boxset instead of individual volumes within it.
            # By having the volume_number stored in the name field, it can be edited and renamed for boxsets.
            # TL;DR - volume number is not necessarily accurate for certain DVDs (and a few manga omnibuses)
            item_volume_number = sheet_data[2][i]
            # Extra details field is important for DVDs as we have marked which DVDs need a region 1 DVD player to play
            item_extra_details = sheet_data[4][i]

            # Create the Item model instance.
            item = Item()
            item.media_type = item_media_type
            item.details = item_extra_details
            # See the long comment above about volume numbers
            item.name = 'Volume {0}'.format(item_volume_number)

            if series_anilist:
                values = re.split(r'/', re.sub(r'(https://)*(www\.)*(anilist.co/)*', '', str(series_anilist)))
                api_id = values[1]
                try:
                    show = Series.objects.get(api_id=api_id)
                except Series.DoesNotExist:
                    # Make series
                    new_series = Series()
                    new_series.auto_populate_data = True
                    new_series.anilist_link = series_anilist
                    try:
                        new_series.save()
                        show = new_series
                    except ValidationError:
                        update_sheet(5, i + 1, "Error with anilist url")
                        show = None
                item.parent_series = show
            else:
                # In this case, we still need to create a Series object for the Item, but we don't have the advantage
                # of being able to just get all the data. From the information provided from the spreadsheet we can get,
                # two different bits of information, the series type anime and manga (for consistency count Light
                # Novels as manga) and the series title.
                new_series = Series()
                # Assume the spreadsheet has english titles
                new_series.title_english = series_title
                # Get the media type based on the type of item. DVD or BD means anime, Manga or Light Novel means manga
                # the media type needs to be lowercase for consistency with the auto-populated Series objects
                if item_media_type in ['BD', 'DVD']:
                    new_series.series_type = 'anime'
                else:
                    # Assuming we don't have any other types of media (We don't as of October 2020)
                    new_series.series_type = 'manga'

                new_series.save()
                item.parent_series = new_series

            # Save Item
            item.save()
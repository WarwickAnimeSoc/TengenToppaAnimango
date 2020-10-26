import time
import gspread
import re
from oauth2client.service_account import ServiceAccountCredentials

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from apps.karaoke.models import Song
from apps.showings.models import Series


def get_spreadsheet_data():
    # Load in the scope and the details of API credentials
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('apps/karaoke/management/commands/authdetails.json',
                                                                   scope)
    client = gspread.authorize(credentials)

    # Select the right spreadsheet and the sheet that the data is on
    sheet = client.open("Karaoke List Import").sheet1

    # Return the values that we need for later
    # [0] = Name of artist, [1] = Name of song, [2] = Anilist link of related Anime (if it exists)
    sheet_data = [sheet.col_values(1), sheet.col_values(2), sheet.col_values(3)]
    return sheet_data


# Updates the spreadsheet at the specified position
def update_sheet(x, y, value):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('apps/karaoke/management/commands/authdetails.json',
                                                                   scope)
    client = gspread.authorize(credentials)

    sheet = client.open("Karaoke List Import").sheet1
    sheet.update_cell(y, x, value)


# This command was mostly taken from the library update command from the old aniMango site
# This command should only be needed once, which is to populate the karaoke lists as it was at the time I created the
# karaoke spreadsheet (Summer 2020) after the initial import songs should be added either via the requests section of
# the site, or thought the django admin
class Command(BaseCommand):
    help = 'Imports the karaoke list from a google spreadsheet'

    def handle(self, *args, **options):
        sheet_data = get_spreadsheet_data()

        # Iterate through all songs
        for i in range(0, len(sheet_data[0])):
            song_artist = sheet_data[0][i]
            song_title = sheet_data[1][i]
            try:
                anilist_url = sheet_data[2][i]
            except IndexError:
                anilist_url = None

            # Sleep for a short period of time to ensure we do not get rate limited... Running time for this command
            # is fairly slow as a result of this.
            time.sleep(.25)

            # Add song to the website if it does not exits
            try:
                song = Song()
                song.artist = song_artist
                song.title = song_title

                # Add show if needed
                if anilist_url:
                    values = re.split(r'/', re.sub(r'(https://)*(www\.)*(anilist.co/)*', '', str(anilist_url)))
                    api_id = values[1]
                    try:
                        show = Series.objects.get(api_id=api_id)
                    except Series.DoesNotExist:
                        # Make series
                        new_series = Series()
                        new_series.auto_populate_data = True
                        new_series.anilist_link = anilist_url
                        try:
                            new_series.save()
                            show = new_series
                        except ValidationError:
                            update_sheet(4, i + 1, "Error with anilist url")
                            show = None
                    song.related_series = show
                try:
                    song.save()
                except IntegrityError as e:
                    print("Failed to add {0}-{1} -> Duplicate entry".format(song_artist, song_title))
            except RuntimeError as e:
                update_sheet(4, i + 1, "Runtime error")

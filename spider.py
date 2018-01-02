#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime

import dropbox
import regex
from apscheduler.schedulers.blocking import BlockingScheduler
from dropbox.exceptions import ApiError
from dropbox.files import WriteMode

from helper import *

PAGE_URL = 'http://nhackhongloi.org'

DATABASE_FILE = 'songs.db'

PLAYLIST_PATTERN = regex.compile(r'title:"([^"]+)"[^=]+=(\d+)[^(]+\("([^"]+)"\)', regex.IGNORECASE)

sched = BlockingScheduler()

"""
Username: drobomusic@muimail.com
Password: 123456
"""

DROPBOX_ACCESS_TOKEN = 'DObvzyN9nNAAAAAAAAAACUNw2YU6lfJUEXOWzy1eUDpAtqG9r9HnPaXiPo0z7i0Q'

DROPBOX = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

DROPBOX_BASE_PATH = '/Instrumental Music'

DROPBOX_DB_PATH = DROPBOX_BASE_PATH + '/' + DATABASE_FILE


def get_playlist_dict(timeout=15):
    playlist_dict = {}
    try:
        response = requests.get(url=PAGE_URL, timeout=timeout)
        if response.status_code == requests.codes.ok:
            items = PLAYLIST_PATTERN.findall(response.content.decode('UTF-8'))
            for item in items:
                playlist_dict[item[1]] = {
                    'name': item[0],
                    'url': item[2]
                }
    except Exception as e:
        debug(e)
    return playlist_dict


def get_distinct_song_ids(old_playlist_dict, new_playlist_dict):
    if new_playlist_dict is None or len(new_playlist_dict) == 0:
        return None

    old_song_ids = []
    if old_playlist_dict:
        old_song_ids = old_playlist_dict.keys()

    distinct_song_ids = list(set(new_playlist_dict.keys()) - set(old_song_ids))
    return distinct_song_ids if len(distinct_song_ids) > 0 else None


@sched.scheduled_job('cron', hour=22)
def sync():
    try:
        debug('Running:', str(datetime.now()))

        # Check authentication credentials
        DROPBOX.users_get_current_account()

        # Get old playlist
        try:
            old_playlist_dict = read_json(DATABASE_FILE)
        except AssertionError:
            old_playlist_dict = {}

        # Get new playlist
        debug('Fetching new songs...')
        new_playlist_dict = get_playlist_dict()
        debug('Number of songs: %d' % len(new_playlist_dict))

        # Get distinct song indices
        distinct_song_ids = get_distinct_song_ids(old_playlist_dict, new_playlist_dict)
        debug('%d new songs' % len(distinct_song_ids))

        songs_db = {}
        if distinct_song_ids:
            # Upload all songs to the new folder
            for i in distinct_song_ids:
                debug('Processing file: %s - %s' % (i, new_playlist_dict[i]['name']))
                try:
                    debug('--Downloading file')
                    song_data = download_file(url=PAGE_URL + '/' + new_playlist_dict[i]['url'])
                    if song_data:
                        file_name = DROPBOX_BASE_PATH + '/%s - %s.mp3' % (i, new_playlist_dict[i]['name'])

                        debug('--Uploading file')
                        DROPBOX.files_upload(song_data, file_name, WriteMode.overwrite, mute=True)

                        songs_db[i] = {
                            'name': new_playlist_dict[i]['name'],
                            'file': file_name
                        }
                        debug('--OK')
                    else:
                        debug('--Download failed:', PAGE_URL + '/' + new_playlist_dict[i]['url'])
                except Exception as err:
                    debug('--Upload failed:', err)
                    if isinstance(err, ApiError) and err.error.is_path() and \
                            err.error.get_path().reason.is_insufficient_space():
                        break
                    continue

            full_songs_db = {**old_playlist_dict, **songs_db}
            # Save database file
            write_json(full_songs_db, DATABASE_FILE)

            # Upload database file to Dropbox
            try:
                DROPBOX.files_upload(
                    json.dumps(full_songs_db, indent=4, ensure_ascii=False).encode('UTF-8'), DROPBOX_DB_PATH,
                    WriteMode.overwrite, mute=True)
            except ApiError as apierr:
                debug(apierr)

        debug('Done: %d songs' % len(songs_db))
    except Exception as e:
        debug(e)


def main():
    debug('Scheduling:', str(datetime.now()))
    sched.start()


if __name__ == '__main__':
    main()

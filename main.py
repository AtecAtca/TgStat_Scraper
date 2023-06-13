from typing import Any, Iterator

from Scraper.categories import scrape_categories, save_categories, read_categories
from Scraper.channels import scrape_channels, save_channels, read_channels
from Scraper.channel_info import scrape_info
from Scraper.channel_info import ChannelNotFound, AuthorisationError
import os
import csv


def save_checkpoint(checkpoint):
    with open('checkpoint.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(checkpoint)


def read_checkpoint():
    try:
        with open('checkpoint.csv', 'r') as f:
            reader = csv.reader(f)
            for r in reader:
                return r
    except FileNotFoundError:
        return None


def save_output(data):
    output_filename = 'output.csv'
    file_exists = os.path.exists(output_filename)
    with open(output_filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def prepare_data(channels_path, checkpoint, file_list=None):

    if checkpoint is None:
        file_list = os.listdir(channels_path)
    else:
        file_list = os.listdir(channels_path)
        checkpoint_index = file_list.index(checkpoint[0])
        file_list = file_list[checkpoint_index:]

    for filename in file_list:
        if checkpoint is not None:
            channels_data = iter(read_channels(channels_path + filename, checkpoint))
            checkpoint = None
        else:
            channels_data = iter(read_channels(channels_path + filename, checkpoint=None))

        for channel_data in channels_data:

            try:
                channel_info = scrape_info(channel_data, category=filename.split('.csv')[0])
            except ChannelNotFound:
                print(f'404 ERROR: {channel_data}')
            except AuthorisationError:
                print(f'429 ERROR: Need authorisation.')
                return filename, channel_data
            else:
                print(f'SAVED: {channel_data}')
                save_output(channel_info)


def main():
    data_path = 'Data\\csv\\'
    categories_dir = 'Categories\\categories.csv'
    categories_path = data_path + categories_dir
    channels_dir = 'Channels\\'
    channels_path = data_path + channels_dir


    #categories = scrape_categories()
    #categories = save_categories(categories, categories_path)
    #categories = iter(read_categories(categories_path))


    #for category in categories:
    #    name, href, count = category
    #    channels = scrape_channels(href)
    #    channels = save_channels(channels, f'{channels_path}{href}.csv')

    checkpoint = prepare_data(channels_path, checkpoint=read_checkpoint())
    if checkpoint is not None:
        save_checkpoint(checkpoint)

if __name__ == '__main__':
    main()

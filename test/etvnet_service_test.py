import test_helper

import unittest
import json

from etvnet_service import EtvnetService
from config import Config

class EtvnetServiceTest(unittest.TestCase):
    def setUp(self):
        config = Config("../etvnet.config")

        self.service = EtvnetService(config)

    def test_channels(self):
        result = self.service.get_channels()

        print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

        for value in result['data']:
            print(value['name'])

    def test_archive(self):
        result = self.service.get_archive(channel=3)

        # print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']['media']), 0)

        print(json.dumps(result['data']['media'], indent=4))

    def test_genres(self):
        result = self.service.get_genres()

        # print(json.dumps(result, indent=4))

        for item in result['data']:
            print(item['id'])
            print(item['name'])

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_blockbusters(self):
        result = self.service.get_blockbusters()

        #print(json.dumps(result, indent=4))

        for item in result['data']['media']:
            print(item['type'])
            print(item['id'])
            print(item['name'])

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']['media']), 0)

    # def test_serials(self):
    #     result = self.service.get_serials()
    #
    #     #print(json.dumps(result, indent=4))
    #
    #     for item in result['data']['media']:
    #         print(item['type'])
    #         print(item['id'])
    #         print(item['name'])
    #
    #     self.assertEqual(result['status_code'], 200)
    #     self.assertNotEqual(len(result['data']['media']), 0)

    # def test_movies(self):
    #     result = self.service.get_movies()
    #
    #     #print(json.dumps(result, indent=4))
    #
    #     for item in result['data']['media']:
    #         print(item['type'])
    #         print(item['id'])
    #         print(item['name'])
    #
    #     self.assertEqual(result['status_code'], 200)
    #     self.assertNotEqual(len(result['data']['media']), 0)

    def test_search(self):
        query= "news"
        result = self.service.search(query=query)

        print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_pagination(self):
        query= "news"
        result = self.service.search(query=query, page=1, per_page=20)

        #print(json.dumps(result, indent=4))

        pagination = result['data']['pagination']

        self.assertEqual(pagination['has_next'], True)
        self.assertEqual(pagination['has_previous'], False)
        self.assertEqual(pagination['page'], 1)

        result = self.service.search(query=query, page=2)

        #print(json.dumps(result, indent=4))

        pagination = result['data']['pagination']

        self.assertEqual(pagination['has_next'], True)
        self.assertEqual(pagination['has_previous'], True)
        self.assertEqual(pagination['page'], 2)

    def test_new_arrivals(self):
        result = self.service.get_new_arrivals()

        print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_get_url(self):
        id = '580162' # 329678
        bitrate = '1200'
        format = 'mp4'

        url_data = self.service.get_url(id, bitrate=bitrate, format=format, protocol='hls')

        print('Media Url: ' + url_data['url'])

        #print('Play list:\n' + self.service.get_play_list(url_data['url']))

    def test_media_object(self):
        result = self.service.get_archive(channel=3)

        #print(json.dumps(result, indent=4))

        media_object = None

        for item in result['data']['media']:
            type = item['type']

            if type == 'MediaObject':
                media_object = item
                break

        print(json.dumps(media_object, indent=4))

        bitrates = self.service.bitrates(media_object['files'])

        if 'mp4' in bitrates.keys():
            format = 'mp4'
        else:
            format = 'wmv'

        bitrate = bitrates[format][0]

        url_data = self.service.get_url(media_object['id'], bitrate=bitrate, format=format)

        self.print_url_data(url_data, bitrates)

        new_url_data = self.service.http_request(url_data['url']).read()

        print new_url_data

    def test_container(self):
        result = self.service.get_archive(channel=3)

        #print(json.dumps(result, indent=4))

        container = None

        for item in result['data']['media']:
            type = item['type']

            if type == 'Container':
                container = item
                break

        #print(json.dumps(container, indent=4))

        children = self.service.get_children(container['id'])

        #print(json.dumps(children, indent=4))

        first_media_object = None

        for child in children['data']['children']:
            if child['type'] == 'MediaObject':
                first_media_object = child

        print(json.dumps(first_media_object, indent=4))

        bitrates = self.service.bitrates(first_media_object['files'])

        bitrate = bitrates['mp4'][2]

        url_data = self.service.get_url(first_media_object['id'], bitrate=bitrate, format='mp4')

        self.print_url_data(url_data, bitrates)

    def print_url_data(self, url_data, bitrates):
        print("Available bitrates:")

        if 'wmv' in bitrates.keys():
            print("wmv: (" + " ".join(str(x) for x in bitrates['wmv']) + ")")

        if 'mp4' in bitrates.keys():
            print("mp4: (" + " ".join(str(x) for x in bitrates['mp4']) + ")")

        print('Format: ' + url_data['format'])
        print('Bitrate: ' + str(url_data['bitrate']))
        print('Protocol: ' + str(url_data['protocol']))

        print('Media Url: ' + url_data['url'])

    def test_get_bookmarks(self):
        result = self.service.get_bookmarks()

        print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_get_folders(self):
        result = self.service.get_folders()

        print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_get_bookmark(self):
        bookmarks = self.service.get_bookmarks()

        bookmark = bookmarks['data']['bookmarks'][0]

        result = self.service.get_bookmark(id=bookmark['id'])

        print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_get_topics(self):
        for topic in EtvnetService.TOPICS:
            result = self.service.get_topic_items(topic)

            #print(json.dumps(result, indent=4))

            self.assertEqual(result['status_code'], 200)
            self.assertNotEqual(len(result['data']), 0)

    def test_get_video_resolution(self):
        print self.service.bitrate_to_resolution(1500)

    def test_live_channels(self):
        result = self.service.get_live_channels()

        #print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

        for value in result['data']:
            print(value['id'])
            print(value['name'])
            print(value['icon'])
            print(value['live_format'])
            print(value['files'])

    def test_live_channel(self):
        result = self.service.get_live_channels()

        #print(json.dumps(result, indent=4))

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

        channel = result['data'][0]

        url_data = self.service.get_url(None, channel_id=channel['id'], bitrate='400', format='mp4', live=True, offset=channel['offset'])

        print(url_data)

        self.assertNotEqual(url_data['url'], None)

    def test_live_schedule(self):
        result = self.service.get_live_channels()
        channel = result['data'][0]

        result = self.service.get_live_schedule(live_channel_id=channel['id'])

        #print(json.dumps(result, indent=4))

        for value in result['data']:
            print(value['rating'])
            print(value['media_id'])
            print(value['name'])
            print(value['finish_time'])
            print(value['start_time'])
            print(value['current_show'])
            print(value['categories'])
            print(value['efir_week'])
            print(value['channel'])
            print(value['description'])

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

    def test_live_categories(self):
        result = self.service.get_live_categories()

        #print(json.dumps(result, indent=4))

        for value in result['data']:
            print(value['id'])
            print(value['name'])

        self.assertEqual(result['status_code'], 200)
        self.assertNotEqual(len(result['data']), 0)

if __name__ == '__main__':
    unittest.main()
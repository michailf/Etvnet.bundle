import sys
import urllib
import json
from lxml import html

try:
    from urllib2 import Request, urlopen
except:
    from urllib.request import Request, urlopen

class HttpService():
    def build_url(self, path, **params):
        url = path

        for key, val in params.items():
            if val is not None:
                delimiter = ('?', '&')['?' in url]
                url = url + delimiter + '%s=%s' % (key, urllib.quote(str(val)))

        return url

    def http_request(self, url, headers=None, data=None, method=None):
        if data is not None:
            data = urllib.urlencode(data)
            request = Request(url, data)
        else:
            request = Request(url)

        if method is not None:
            request.get_method = lambda: method

        if headers:
            for key, value in headers.items():
                request.add_header(key, value)

        return urlopen(request)

    def get_content(self, response):
        content = response.read()

        if sys.version_info.major == 3:
            return content.decode('utf-8')
        else:
            return content

    def get_play_list(self, url):
        path = url.split('/')
        path.pop()
        path = '/'.join(path)

        lines = self.http_request(url).read().splitlines()
        new_lines = []

        for line in lines:
            if line[:1] == '#':
                new_lines.append(line)
            else:
                new_lines.append(path + '/' + line)

        return "\n".join(new_lines)

    def fetch_document(self, url):
        response = self.http_request(url)

        content = response.read()

        return self.to_document(content)

    def to_document(self, buffer):
        return html.fromstring(buffer)

    def to_json(self, buffer):
        if not buffer:
            buffer = "{}"

        return json.loads(buffer)

    def bitrate_to_resolution(self, bitrate):
        # table = {
        #     '1080': [3000, 6000],
        #     '720': [1500, 4000],
        #     '480': [500, 2000],
        #     '360': [400, 1000],
        #     '240': [300, 700]
        # }
        # table = {
        #     '1080': [2000, 3000],
        #     '720': [1000, 1800],
        #     '480': [500, 900],
        #     '360': [350, 450],
        #     '240': [000, 300]
        # }
        table = {
            '1080': [1500, 3000],
            '720': [500, 1499],
            '480': [350, 499],
            '360': [200, 349],
            '240': [000, 199]
        }

        video_resolutions = []

        for key, values in table.iteritems():
            if bitrate in range(values[0], values[1]):
                video_resolutions.append(key)

        return video_resolutions

import json
import urllib

import util
import common
import pagination
import bookmarks

@route(common.PREFIX + '/archive_menu')
def GetArchiveMenu():
    oc = ObjectContainer(title2=unicode(L('Archive')))

    oc.add(DirectoryObject(key=Callback(GetChannels), title=unicode(L('Channels'))))

    result = service.get_genres()

    for genre in result['data']:
        if genre['id'] == 207: # blockbusters
            continue

        key = Callback(HandleGenre, id=genre['id'], name=genre['name'])
        title = genre['name']

        oc.add(DirectoryObject(key=key, title=title))

    oc.add(InputDirectoryObject(
        key = Callback(SearchMovies),
        title = unicode(L("Movies Search")),
        prompt = unicode(L('Search on Etvnet')),
        thumb = R(common.SEARCH_ICON)))

    return oc

@route(common.PREFIX + '/search_movies')
def SearchMovies(query=None, page=1, **params):
    response = service.search(query=query, per_page=util.get_elements_per_page(), page=page)

    oc = ObjectContainer(title2=unicode(L('Movies Search')))

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=SearchMovies, query=query, params=params)

    if len(oc) < 1:
        return util.no_contents('Movies Search')

    return oc

@route(common.PREFIX + '/topics_menu')
def GetTopicsMenu():
    oc = ObjectContainer(title2=unicode(L('Topics')))

    for topic in service.TOPICS:
        oc.add(DirectoryObject(
            key=Callback(HandleTopic, id=topic),
            title=unicode(L(topic))
        ))

    return oc

@route(common.PREFIX + '/topic')
def HandleTopic(id, page=1, **params):
    oc = ObjectContainer(title2=unicode(L(id)))

    response = service.get_topic_items(id, page=page, per_page=util.get_elements_per_page())

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], callback=HandleTopic, id=id, page=page, params=params)

    return oc

@route(common.PREFIX + '/channels')
def GetChannels():
    oc = ObjectContainer(title2=unicode(L('Channels')))

    response = service.get_channels()

    for channel in response['data']:
        if channel['id'] == 158: # cool movies
            continue

        key = Callback(HandleChannel, id=channel['id'], name=channel['name'])
        title = unicode(channel['name'])

        oc.add(DirectoryObject(key=key, title=title))

    return oc

@route(common.PREFIX + '/channel')
def HandleChannel(id, name, page=1, **params):
    oc = ObjectContainer(title2=unicode(name))

    response = service.get_archive(channel_id=id, per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=HandleChannel, id=id, name=name, params=params)

    return oc

@route(common.PREFIX + '/genre')
def HandleGenre(id, name, page=1, **params):
    oc = ObjectContainer(title2=unicode(name))

    response = service.get_archive(genre=int(id), per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=HandleGenre, id=id, name=name, params=params)

    return oc

@route(common.PREFIX + '/blockbusters')
def GetBlockbusters(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('Blockbusters')))

    response = service.get_blockbusters(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetBlockbusters, params=params)

    return oc

@route(common.PREFIX + '/cool_movies')
def GetCoolMovies(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('Cool Movies')))

    response = service.get_cool_movies(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetCoolMovies, params=params)

    return oc

@route(common.PREFIX + '/new_arrivals')
def GetNewArrivals(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('New Arrivals')))

    response = service.get_new_arrivals(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetNewArrivals)

    return oc

@route(common.PREFIX + '/history')
def GetHistory(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('History')))

    response = service.get_history(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetHistory, params=params)

    return oc

def HandleMediaList(response, in_queue=False):
    list = []

    for media in response:
        type = media['type']
        id = media['id']
        name = media['name']
        thumb = media['thumb']

        if type == 'Container':
            key = Callback(HandleChildren, id=id, name=name, thumb=thumb, in_queue=in_queue)

            list.append(DirectoryObject(key=key, title=name, thumb=thumb))
        else:
            if type == 'MediaObject':
                key = Callback(HandleChild,
                    id = id,
                    name = name,
                    thumb = thumb,
                    rating_key = media['rating'],
                    description = media['description'],
                    duration = media['duration'],
                    year = media['year'],
                    on_air = media['on_air'],
                    index = media['series_num'],
                    files = json.dumps(media['files']
                ))

                watch_status = media['watch_status']

                if watch_status == 1:
                    name = "~ " + name
                elif watch_status == 2:
                    name = "* " + name

                list.append(DirectoryObject(key=key, title=name, thumb=thumb))

    return list

@route(common.PREFIX + '/children')
def HandleChildren(id, name, thumb, in_queue=False, page=1, dir='desc'):
    oc = ObjectContainer(title2=unicode(name))

    response = service.get_children(int(id), per_page=util.get_elements_per_page(), page=page, dir=dir)

    for media in HandleMediaList(response['data']['children'], in_queue=in_queue):
        oc.add(media)

    bookmarks.append_controls(oc, id=id, name=name, thumb=thumb)
    append_sorting_controls(oc, HandleChildren, id=id, name=name, thumb=thumb, in_queue=in_queue, page=page, dir=dir)

    pagination.append_controls(oc, response['data'], callback=HandleChildren, id=id, name=name, thumb=thumb,
                               in_queue=in_queue, page=page, dir=dir)

    return oc

@route(common.PREFIX + '/child', container=bool)
def HandleChild(id, name, thumb, rating_key, description, duration, year, on_air, index, files, container=False, **params):
    oc = ObjectContainer(title2=unicode(name))

    oc.add(MetadataObjectForURL(id, 'movie', name, thumb, rating_key, description, duration, year, on_air, index, files))

    if str(container) == 'False':
        bookmarks.append_controls(oc, id=id, name=name, thumb=thumb, rating_key=rating_key,
            description=description, duration=duration, year=year, on_air=on_air, files=files, container=container)

    return oc

def append_sorting_controls(oc, handler, **params):
    if params['dir'] == 'asc':
        params['dir'] = 'desc'
    else:
        params['dir'] = 'asc'

    oc.add(DirectoryObject(
            key=Callback(handler, **params),
            title=unicode(L('Sort Items')),
            thumb="thumb"
    ))

def originally_available_at(on_air):
    return Datetime.ParseDate(on_air.replace('+', ' ')).date()

def MetadataObjectForURL(id, media_type, name, thumb, rating_key, description, duration, year, on_air, index, files):
    video = builder.build_metadata_object(media_type=media_type, name=name, year=year, index=index)

    video.rating_key = rating_key
    video.thumb = thumb
    video.duration = int(duration)*60*1000
    video.summary = unicode(description)
    video.originally_available_at = originally_available_at(on_air)

    video.key = Callback(HandleChild, id=id, name=name, thumb=thumb,
                         rating_key=rating_key, description=description, duration=duration, year=year,
                         on_air=on_air, index=index, files=files, container=True)

    files = json.loads(urllib.unquote_plus(files))

    video.items.extend(MediaObjectsForURL(files=files, media_id=id))

    return video

def MediaObjectsForURL(files, media_id):
    items = []

    for format, bitrates in service.bitrates(files, util.get_format(), util.get_quality_level()).iteritems():
        media_objects = []

        for bitrate in sorted(bitrates, reverse=True):
            play_callback = Callback(PlayVideo, media_id=media_id, bitrate=bitrate, format=str(format))

            media_object = builder.build_media_object(play_callback)

            media_objects.append(media_object)

        items.extend(media_objects)

    return items

@indirect
@route(common.PREFIX + '/play_video')
def PlayVideo(media_id, bitrate, format):
    response = service.get_url(media_id=media_id, format=format, bitrate=bitrate, other_server=util.other_server())

    url = response['url']

    if not url:
        util.no_contents()
    else:
        # new_url = Callback(Playlist, url=url)

        return IndirectResponse(MovieObject, key=HTTPLiveStreamURL(url))

@route(common.PREFIX + '/Playlist.m3u8')
def Playlist(url):
    return service.get_play_list(url)

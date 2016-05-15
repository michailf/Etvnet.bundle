import json
import urllib

import util
import constants
import pagination
import bookmarks

@route(constants.PREFIX + '/archive_menu')
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
        thumb = R(constants.SEARCH_ICON)))

    return oc

@route(constants.PREFIX + '/search_movies')
def SearchMovies(query=None, page=1, **params):
    response = service.search(query=query, per_page=util.get_elements_per_page(), page=page)

    oc = ObjectContainer(title2=unicode(L('Movies Search')))

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=SearchMovies, query=query, params=params)

    if len(oc) < 1:
        return util.no_contents('Movies Search')

    return oc

@route(constants.PREFIX + '/topics_menu')
def GetTopicsMenu():
    oc = ObjectContainer(title2=unicode(L('Topics')))

    for topic in service.TOPICS:
        oc.add(DirectoryObject(
            key=Callback(HandleTopic, id=topic),
            title=unicode(L(topic))
        ))

    return oc

@route(constants.PREFIX + '/topic')
def HandleTopic(id, page=1, **params):
    oc = ObjectContainer(title2=unicode(L(id)))

    response = service.get_topic_items(id, page=page, per_page=util.get_elements_per_page())

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], callback=HandleTopic, id=id, page=page, params=params)

    return oc

@route(constants.PREFIX + '/channels')
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

@route(constants.PREFIX + '/channel')
def HandleChannel(id, name, page=1, **params):
    oc = ObjectContainer(title2=unicode(name))

    response = service.get_archive(channel_id=id, per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=HandleChannel, id=id, name=name, params=params)

    return oc

@route(constants.PREFIX + '/genre')
def HandleGenre(id, name, page=1, **params):
    oc = ObjectContainer(title2=unicode(name))

    response = service.get_archive(genre=int(id), per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=HandleGenre, id=id, name=name, params=params)

    return oc

@route(constants.PREFIX + '/blockbusters')
def GetBlockbusters(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('Blockbusters')))

    response = service.get_blockbusters(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetBlockbusters, params=params)

    return oc

@route(constants.PREFIX + '/cool_movies')
def GetCoolMovies(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('Cool Movies')))

    response = service.get_cool_movies(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetCoolMovies, params=params)

    return oc

@route(constants.PREFIX + '/new_arrivals')
def GetNewArrivals(page=1, **params):
    oc = ObjectContainer(title2=unicode(L('New Arrivals')))

    response = service.get_new_arrivals(per_page=util.get_elements_per_page(), page=page)

    for media in HandleMediaList(response['data']['media']):
        oc.add(media)

    pagination.append_controls(oc, response['data'], page=page, callback=GetNewArrivals)

    return oc

@route(constants.PREFIX + '/history')
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

@route(constants.PREFIX + '/children')
def HandleChildren(id, name, thumb, operation=None, in_queue=False, page=1, dir='desc'):
    oc = ObjectContainer(title2=unicode(name))

    if operation == 'add':
        service.add_bookmark(id)
    elif operation == 'remove':
        service.remove_bookmark(id)

    response = service.get_children(int(id), per_page=util.get_elements_per_page(), page=page, dir=dir)

    for media in HandleMediaList(response['data']['children'], in_queue=in_queue):
        oc.add(media)

    bookmarks.append_controls(oc, HandleChildren, id=id, name=name, thumb=thumb, operation=operation)
    append_sorting_controls(oc, HandleChildren, id=id, name=name, thumb=thumb, in_queue=in_queue, page=page, dir=dir)

    pagination.append_controls(oc, response['data'], callback=HandleChildren, id=id, name=name, thumb=thumb,
                               in_queue=in_queue, page=page, dir=dir)

    return oc

@route(constants.PREFIX + '/child', container=bool)
def HandleChild(id, name, thumb, rating_key, description, duration, year, on_air, index,
                files, operation=None, container=False):
    oc = ObjectContainer(title2=unicode(name))

    if operation == 'add':
        service.add_bookmark(id)
    elif operation == 'remove':
        service.remove_bookmark(id)

    if index > 0:
        media_type = "episode"
    else:
        media_type = "movie"

    oc.add(MetadataObjectForURL(id, media_type, name, thumb, rating_key, description, duration, year, on_air, index, files))

    if str(container) == 'False':
        bookmarks.append_controls(oc, HandleChild, id=id, name=name, thumb=thumb,
                                  rating_key=rating_key, description=description, duration=duration, year=year,
                                  on_air=on_air, index=index, files=files, operation=operation, container=container)
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
    metadata_object = builder.build_metadata_object(media_type=media_type, title=name)

    if media_type == 'episode':
        metadata_object.index = int(index)
    else:
        metadata_object.year = year


    metadata_object.rating_key = rating_key

    metadata_object.title = name
    metadata_object.thumb = thumb
    metadata_object.art = thumb
    metadata_object.duration = int(duration)*60*1000
    metadata_object.summary = unicode(description)
    metadata_object.originally_available_at = originally_available_at(on_air)

    metadata_object.key = Callback(HandleChild, id=id, name=name, thumb=thumb,
                         rating_key=rating_key, description=description, duration=duration, year=year,
                         on_air=on_air, index=index, files=files, container=True)

    files = json.loads(urllib.unquote_plus(files))

    metadata_object.items.extend(MediaObjectsForURL(files=files, media_id=id))

    return metadata_object

def MediaObjectsForURL(files, media_id):
    items = []

    # Log(Client.Platform in util.RAW_HLS_CLIENTS)
    # Log(Client.Product) # Plex Web
    # Log(Client.Platform) # Safari

    format = util.get_format()
    quality_level = util.get_quality_level()

    # if Client.Platform == 'Chrome':
    #     quality_level = util.get_quality_level()
    # else:
    #     quality_level = None

    for format, bitrates in service.bitrates(files, format, quality_level).iteritems():
        media_objects = []

        for bitrate in sorted(bitrates, reverse=True):
            #video_resolution = service.bitrate_to_resolution(bitrate)[0]

            play_callback = Callback(PlayVideo, media_id=media_id, bitrate=bitrate, format=str(format))

            config = {
                "video_codec" : VideoCodec.H264,
                "protocol": Protocol.HLS,
                "container": Container.MPEGTS,
                "video_resolution": bitrate
            }

            media_object = builder.build_media_object(play_callback, config)

            media_objects.append(media_object)

        items.extend(media_objects)

    return items

@indirect
@route(constants.PREFIX + '/play_video')
def PlayVideo(media_id, bitrate, format):
    response = service.get_url(media_id=media_id, format=format, bitrate=bitrate, other_server=util.other_server())

    url = response['url']

    if not url:
        util.no_contents()
    else:
        # new_url = Callback(Playlist, url=url)

        return IndirectResponse(MovieObject, key=HTTPLiveStreamURL(url))

@route(constants.PREFIX + '/Playlist.m3u8')
def Playlist(url):
    return service.get_play_list(url)

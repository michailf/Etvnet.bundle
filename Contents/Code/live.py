import json
import datetime
import urllib

import util
import common
import pagination
import archive

@route(common.PREFIX + '/live_channels_menu')
def GetLiveChannelsMenu():
    oc = ObjectContainer(title2=unicode(L('Live')))

    oc.add(DirectoryObject(key=Callback(GetLiveChannels, title=L('All Channels')), title=unicode(L('All Channels'))))
    oc.add(DirectoryObject(key=Callback(GetLiveChannels, title=L('Favorite'), favorite_only=True),
                           title=unicode(L('Favorite'))))

    result = service.get_live_categories()

    for genre in result['data']:
        name = genre['name']
        category = int(genre['id'])

        oc.add(DirectoryObject(
                key=Callback(GetLiveChannels, title=name, category=category),
                title=unicode(name)
        ))

    return oc

@route(common.PREFIX + '/live_channels')
def GetLiveChannels(title, favorite_only=False, category=0, page=1, **params):
    page = int(page)

    oc = ObjectContainer(title2=unicode(title))

    response = service.get_live_channels(favorite_only=favorite_only, category=category)

    for index, media in enumerate(response['data']):
        if index >= (page - 1) * util.get_elements_per_page() and index < page * util.get_elements_per_page():
            id = media['id']
            name = media['name']
            thumb = media['icon']
            files = media['files']

            oc.add(DirectoryObject(
                    key=Callback(GetLiveChannel, name=name, channel_id=id, thumb=thumb, files=json.dumps(files), **params),
                    title=unicode(name),
                    thumb=Resource.ContentsOfURLWithFallback(url=thumb)
            ))

    add_pagination_to_response(response, page)
    pagination.append_controls(oc, response['data'], callback=GetLiveChannels, title=title, favorite_only=favorite_only,
                               page=page, **params)

    return oc

@route(common.PREFIX + '/live_channel')
def GetLiveChannel(name, channel_id, thumb, files, container=False, **params):
    oc = ObjectContainer(title2=unicode(name))

    oc.add(MetadataObjectForURL(name, channel_id, thumb, files))

    if not container:
        oc.add(DirectoryObject(key=Callback(GetSchedule, channel_id=channel_id), title=unicode(L('Schedule'))))

        append_controls(oc, id=channel_id, name=name, thumb=thumb)

    return oc

@route(common.PREFIX + '/schedule')
def GetSchedule(channel_id):
    oc = ObjectContainer(title2=unicode(L('Schedule')))

    default_time = get_moscow_time()

    today = default_time.date()

    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)

    yesterday_result = service.get_live_schedule(live_channel_id=channel_id, date=yesterday)
    today_result = service.get_live_schedule(live_channel_id=channel_id, date=today)
    tomorrow_result = service.get_live_schedule(live_channel_id=channel_id, date=tomorrow)

    add_schedule(oc, channel_id, default_time, yesterday_result['data'])
    add_schedule(oc, channel_id, default_time, today_result['data'])
    add_schedule(oc, channel_id, default_time, tomorrow_result['data'])

    return oc

def add_schedule(oc, channel_id, default_time, list):
    channels = service.get_live_channels()['data']

    channel = find_channel(int(channel_id), channels)

    offset = service.get_offset(util.get_time_shift())
    time_delta = datetime.timedelta(hours=offset)

    files = channel['files']

    for media in list:
        start_time = get_time(media['start_time'])
        finish_time = get_time(media['finish_time'])

        current_title = in_time_range(default_time - time_delta, start_time, finish_time)

        if media['media_id']:
            if media['rating']:
                rating = media['rating']
            else:
                rating = 'unknown'

            key = Callback(archive.HandleChild,
                id = media['media_id'],
                name = media['name'],
                thumb = 'thumb',
                rating_key = rating,
                description = media['description'],
                duration = 0,
                year = 0,
                on_air = media['start_time'],
                index = 0,
                files = json.dumps(files)
            )

            title = get_schedule_title(media['name'], start_time, finish_time, current_title=current_title)

            oc.add(DirectoryObject(key=key, title=unicode(title)))
        else:
            select_key = Callback(GetSchedule, channel_id=channel_id)

            title = get_schedule_title(media['name'], start_time, finish_time, current_title=current_title, available=False)

            oc.add(DirectoryObject(key=select_key, title=unicode(title)))

def in_time_range(actual_time, start_time, finish_time):
    in_range = False

    if actual_time.day == start_time.day:
        if actual_time.hour == finish_time.hour:
            if actual_time.minute <= finish_time.minute:
                in_range = True
        elif actual_time.hour == start_time.hour:
            if actual_time.minute >= start_time.minute:
                return True

    return in_range

def get_schedule_title(name, start_time, finish_time, current_title=False, available=True):
    if current_title:
        left_sep = "---> "
        right_sep = " <---"
    else:
        left_sep = ""
        right_sep = ""

    if not available:
        left_sep = left_sep  + " ***"
        right_sep = right_sep + " ***"

    prefix = str(start_time)[11:16] + " - " + str(finish_time)[11:16] + " : "

    return prefix + left_sep + name + right_sep

def get_time(value):
    return datetime.datetime.strptime(value.replace('T', ' '), '%Y-%m-%d %H:%M:%S')

def get_moscow_time():
    utc_datetime = datetime.datetime.utcnow()

    time = datetime.datetime.strptime(str(utc_datetime), '%Y-%m-%d %H:%M:%S.%f')

    return time + datetime.timedelta(hours=3)

def append_controls(oc, **params):
    favorite_channels = service.get_live_channels(favorite_only=True)['data']

    favorite_channel = find_channel(int(params['id']), favorite_channels)

    if favorite_channel:
        oc.add(DirectoryObject(
                key=Callback(HandleRemoveFavoriteChannel, type=type, **params),
                title=unicode(L('Remove Favorite')),
                thumb=R(common.REMOVE_ICON)
        ))
    else:
        oc.add(DirectoryObject(
                key=Callback(HandleAddFavoriteChannel, type=type, **params),
                title=unicode(L('Add Favorite')),
                thumb=R(common.ADD_ICON)
        ))

def find_channel(id, favorite_channels):
    found = None

    for media in favorite_channels:
        if id == media['id']:
            found = media
            break

    return found

@route(common.PREFIX + '/add_favorite_channel')
def HandleAddFavoriteChannel(**params):
    service.add_favorite_channel(params['id'])

    return ObjectContainer(header=unicode(L(params['name'])), message=unicode(L('Favorite Added')))

@route(common.PREFIX + '/remove_favorite_channel')
def HandleRemoveFavoriteChannel(**params):
    service.remove_favorite_channel(params['id'])

    return ObjectContainer(header=unicode(L(params['name'])), message=unicode(L('Favorite Removed')))

def add_pagination_to_response(response, page):
    pages = len(response['data']) / util.get_elements_per_page()

    response['data'] = {'pagination': {
        'page': page,
        'pages': pages,
        'has_next': page < pages,
        'has_previous': page > 1
    }}

def MetadataObjectForURL(name, channel_id, thumb, files):
    video = MovieObject(
        rating_key='rating_key',
        title=unicode(name),
        thumb=thumb,
        art=thumb
    )

    video.key = Callback(GetLiveChannel, name=name, channel_id=channel_id, thumb=thumb, files=files, container=True)

    offset = service.get_offset(util.get_time_shift())

    format ='mp4'
    quality_level = util.get_quality_level()

    # Log(Client.Platform in util.RAW_HLS_CLIENTS)
    # Log(Client.Product)  # Plex Web
    # Log(Client.Platform)  # Safari

    # if Client.Platform == 'Chrome':
    #     quality_level = util.get_quality_level()
    # else:
    #     quality_level = None

    files = json.loads(urllib.unquote_plus(files))

    bitrates = service.bitrates(files, accepted_format=format, quality_level=quality_level)

    video.items.extend(MediaObjectsForURL(bitrates, channel_id, offset, format))

    return video

def MediaObjectsForURL(bitrates, channel_id, offset, format):
    items = []

    media_objects = []

    for bitrate in sorted(bitrates[format], reverse=True):
        play_callback = Callback(PlayLive, channel_id=channel_id, bitrate=bitrate, format=format, offset=offset)

        media_object = builder.build_media_object(play_callback, video_resolution=bitrate, bitrate=bitrate)

        media_objects.append(media_object)

    items.extend(media_objects)

    return items

@indirect
@route(common.PREFIX + '/play_live')
def PlayLive(channel_id, bitrate, format, offset):
    response = service.get_url(None, channel_id=channel_id, bitrate=bitrate, format=format, live=True,
                               offset=offset, other_server=util.other_server())
    url = response['url']

    if not url:
        util.no_contents()
    else:
        return IndirectResponse(MovieObject, key=HTTPLiveStreamURL(url))


@route(common.PREFIX + '/Playlist')
def Playlist(url):
    return service.get_play_list(url)

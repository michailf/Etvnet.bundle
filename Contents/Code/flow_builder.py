def empty_play_back():
    pass

def build_media_objects(play_callback=Callback(empty_play_back)):
    media_objects = []

    media_object = build_media_object(play_callback)

    media_objects.append(media_object)

    return media_objects

def build_media_object(play_callback, **params):
    audio_stream = AudioStreamObject()

    audio_stream.channels = 2

    if 'audio_codec' in params.keys():
        audio_stream.codec = params['audio_codec']
    else:
        audio_stream.codec = AudioCodec.AAC

    if 'bitrate' in params.keys():
        audio_stream.bitrate = params['bitrate']

    video_stream = VideoStreamObject()

    if 'video_codec' in params.keys():
        video_stream.codec = params['video_codec']
    else:
        video_stream.codec = VideoCodec.H264

    part_object = PartObject(
        key=play_callback,
        streams=[audio_stream, video_stream]
    )

    media_object = MediaObject()

    media_object.optimized_for_streaming = True

    if 'protocol' in params.keys():
        media_object.protocol = params['protocol']
    else:
        media_object.protocol = Protocol.HLS

    if 'container' in params.keys():
        media_object.container = params['container']
    else:
        media_object.container = Container.MPEGTS

    if 'video_resolution' in params.keys():
        media_object.video_resolution = params['video_resolution']

    media_object.parts = [part_object]

    return media_object

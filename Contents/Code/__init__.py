PREFIX = '/video/etvnet'ART = 'art-default.jpg'ICON = 'icon-default.png'SEARCH_ICON = 'icon-search.png'OPTIONS_ICON = 'icon-options.png'ADD_ICON = 'icon-add.png'REMOVE_ICON = 'icon-remove.png'import library_bridgelibrary_bridge.bridge.export_object('L', L)library_bridge.bridge.export_object('R', R)library_bridge.bridge.export_object('Log', Log)library_bridge.bridge.export_object('Resource', Resource)library_bridge.bridge.export_object('Datetime', Datetime)library_bridge.bridge.export_object('Core', Core)library_bridge.bridge.export_object('Prefs', Prefs)library_bridge.bridge.export_object('Locale', Locale)library_bridge.bridge.export_object('Callback', Callback)library_bridge.bridge.export_object('AudioCodec', AudioCodec)library_bridge.bridge.export_object('VideoCodec', VideoCodec)library_bridge.bridge.export_object('AudioStreamObject', AudioStreamObject)library_bridge.bridge.export_object('VideoStreamObject', VideoStreamObject)library_bridge.bridge.export_object('DirectoryObject', DirectoryObject)library_bridge.bridge.export_object('PartObject', PartObject)library_bridge.bridge.export_object('MediaObject', MediaObject)library_bridge.bridge.export_object('EpisodeObject', EpisodeObject)library_bridge.bridge.export_object('TVShowObject', TVShowObject)library_bridge.bridge.export_object('MovieObject', MovieObject)library_bridge.bridge.export_object('TrackObject', TrackObject)library_bridge.bridge.export_object('VideoClipObject', VideoClipObject)library_bridge.bridge.export_object('MessageContainer', MessageContainer)library_bridge.bridge.export_object('Container', Container)import utilimport etvnet_plex_serviceimport radio_servicefrom flow_builder import FlowBuilderbuilder = FlowBuilder()service = etvnet_plex_service.EtvnetPlexService()radio_service = radio_service.RadioService()import liveimport archiveimport bookmarksimport radiodef Start():    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")    Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')    Plugin.AddViewGroup('MediaPreview', viewMode='MediaPreview', mediaType='items')    # DirectoryObject.thumb = R(ICON)    DirectoryObject.art = R(ART)    # VideoClipObject.thumb = R(ICON)    VideoClipObject.art = R(ART)    HTTP.CacheTime = CACHE_1HOUR    util.validate_prefs()@handler(PREFIX, 'Etvnet', thumb=ICON, art=ART, allow_sync=True)def MainMenu(autorizationCompleted=False, resetToken=False):    oc = ObjectContainer(title1='Etvnet', art=R(ART))    if resetToken:        service.reset_token()    if not service.check_token():        oc.add(DirectoryObject(            key=Callback(Authorization),            title=unicode(L('Authorize')),            thumb=R(OPTIONS_ICON),        ))        if autorizationCompleted:            oc.header = unicode(L('Authorize'))            oc.message = unicode(L('You must enter code for continue'))        return oc    oc.http_cookies = HTTP.CookiesForURL(service.API_URL)    oc.add(DirectoryObject(key=Callback(live.GetLiveChannelsMenu), title=unicode(L('Live'))))    oc.add(DirectoryObject(key=Callback(archive.GetArchiveMenu), title=unicode(L('Archive'))))    oc.add(DirectoryObject(key=Callback(archive.GetBlockbusters), title=unicode(L('Blockbusters'))))    oc.add(DirectoryObject(key=Callback(archive.GetCoolMovies), title=unicode(L('Cool Movies'))))    oc.add(DirectoryObject(key=Callback(archive.GetNewArrivals), title=unicode(L('New Arrivals'))))    oc.add(DirectoryObject(key=Callback(archive.GetTopicsMenu), title=unicode(L('Topics'))))    oc.add(DirectoryObject(key=Callback(bookmarks.GetBookmarks), title=unicode(L('Bookmarks'))))    oc.add(DirectoryObject(key=Callback(radio.GetRadioMenu), title=unicode(L('Radio'))))    oc.add(DirectoryObject(key=Callback(GetSystemMenu), title=unicode(L('System'))))    oc.add(InputDirectoryObject(key=Callback(archive.SearchMovies), title=unicode(L("Movies Search")),                                thumb=R(SEARCH_ICON)))    return oc@route(PREFIX + '/system_menu')def GetSystemMenu():    oc = ObjectContainer(title2=unicode(L('System')))    oc.add(DirectoryObject(key=Callback(archive.GetHistory), title=unicode(L('History'))))    oc.add(DirectoryObject(key=Callback(MainMenu, autorizationCompleted=True, resetToken=True), title=unicode(L('Reset Token'))))    return oc@route(PREFIX + '/authorization')def Authorization():    return service.authorization(on_authorization_success=OnAuthorizationSuccess,                                 on_authorization_failure=OnAuthorizationFailure)def OnAuthorizationSuccess(user_code, device_code, activation_url, autorizationCompleted=False):    oc = ObjectContainer(title2=unicode(L('Authorize')), no_cache=True)    if autorizationCompleted:        response = service.create_token(device_code=device_code)        if response:            done = response.has_key('access_token')            if not done:                oc.add(DirectoryObject(                    key=Callback(OnAuthorizationSuccess, user_code=user_code, device_code=device_code,                                 activation_url=activation_url, autorizationCompleted=True),                    title=unicode(L('Authorization in progress...')),                    summary=unicode(L('Wait a little')),                ))            else:                oc.add(DirectoryObject(                    key=Callback(MainMenu, autorizationCompleted=True),                    title=unicode(L('Authorization completed')),                    summary=unicode(L('Go to main menu')),                ))                service.config.save(response)            return oc    else:        oc.add(DirectoryObject(            key=Callback(OnAuthorizationSuccess, user_code=user_code, device_code=device_code,                activation_url=activation_url, autorizationCompleted=True),            title=unicode(F('codeIs', user_code)),            summary=unicode(F('enterCodeSite', user_code, activation_url)),            tagline=activation_url,        ))        oc.add(DirectoryObject(            key=Callback(OnAuthorizationSuccess, user_code=user_code, device_code=device_code,                         activation_url=activation_url, autorizationCompleted=True),            title=unicode(L('Authorize')),            summary=unicode(L('Complete authorization')),        ))        return ocdef OnAuthorizationFailure():    return ObjectContainer(        header=unicode(L('Error')),        message=unicode(L('Service temporarily unavailable'))    )
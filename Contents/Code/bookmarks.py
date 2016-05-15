import constants
import archive

def append_controls(oc, handler, **params):
    bookmark = service.get_bookmark(params['id'])

    if bookmark:
        params['operation'] = 'remove'
        oc.add(DirectoryObject(
                key=Callback(handler, **params),
                title=unicode(L('Remove Bookmark')),
                thumb=R(constants.REMOVE_ICON)
        ))
    else:
        params['operation'] = 'add'
        oc.add(DirectoryObject(
                key=Callback(handler, **params),
                title=unicode(L('Add Bookmark')),
                thumb=R(constants.ADD_ICON)
        ))

@route(constants.PREFIX + '/bookmarks')
def GetBookmarks():
    oc = ObjectContainer(title2=unicode(L('Bookmarks')))

    response = service.get_bookmarks()

    for media in archive.HandleMediaList(response['data']['bookmarks']):
        oc.add(media)

    return oc

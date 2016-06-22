def append_controls(oc, handler, **params):
    bookmark = service.get_bookmark(params['id'])

    if bookmark:
        params['operation'] = 'remove'
        oc.add(DirectoryObject(
                key=Callback(handler, **params),
                title=unicode(L('Remove Bookmark')),
                thumb=R(REMOVE_ICON)
        ))
    else:
        params['operation'] = 'add'
        oc.add(DirectoryObject(
                key=Callback(handler, **params),
                title=unicode(L('Add Bookmark')),
                thumb=R(ADD_ICON)
        ))

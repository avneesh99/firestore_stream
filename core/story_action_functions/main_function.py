from firebase_admin import firestore


def story_action_queue_on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            print(f'Received Document for following request: {change.document.id}')
            document_dict = change.document.to_dict()

            if not checking_valid_document(document_dict=document_dict):
                # TODO: what to do if error
                print('not in right format')
                continue

            db = firestore.client()

            storyId = document_dict['storyId']
            print(storyId)
            try:
                viewer_details_dict = db.collection('UserDetails').document(document_dict['viewerUid']).get().to_dict()
                viewer_username = viewer_details_dict['username']
                viewer_fullname = viewer_details_dict['fullName']
                print(viewer_fullname, viewer_username)
            except Exception as e:
                print(f'Error in getting the viewer details: {e}')
                continue

            # add to self
            try:
                db.collection('Map').document(document_dict['publisherUid']) \
                    .collection('Coordinates').document('self') \
                    .collection('Viewers').document(storyId).update({
                        'viewersList': firestore.ArrayUnion([{
                            'viewerUid': document_dict['viewerUid'],
                            'viewerUsername': viewer_username,
                            'viewerFullName': viewer_fullname
                        }])
                    })

                db.collection('Map').document(document_dict['viewerUid'])\
                    .collection('Coordinates').document('other').update({
                        f'{storyId}.viewed': True
                    })
            except Exception as e:
                print(f'Error while updating story: {e}')

            db.collection('StoryActionQueue').document(change.document.id).delete()

        if change.type.name == 'REMOVED':
            print(f'Removed document {change.document.id}')


def checking_valid_document(document_dict: dict) -> bool:
    try:
        if type(document_dict['viewerUid']) != str or type(document_dict['publisherUid']) != str or type(
                document_dict['storyId']) != str:
            return False
    except Exception as e:
        print(f'Error: {e}')

    return True

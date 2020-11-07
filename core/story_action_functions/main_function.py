from firebase_admin import firestore


def story_action_queue_on_snapshot(col_snapshot, changes, read_time):
    db = firestore.client()
    for change in changes:
        if change.type.name == 'ADDED':
            print('\n')
            print(f'Received Document for following request: {change.document.id}')
            documentDict = change.document.to_dict()

            if not CheckingValidDocument(document_dict=documentDict):
                print('not in right format')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': f'document not in right format'
                })
                db.collection('StoryActionQueue').document(change.document.id).delete()
                continue

            storyId = documentDict['storyId']
            try:
                viewer_details_dict = db.collection('UserDetails').document(documentDict['viewerUid']).get().to_dict()
                viewer_username = viewer_details_dict['username']
                viewer_fullname = viewer_details_dict['fullName']
            except Exception as e:
                print(f'Error in getting the viewer details: {e}')
                continue

            # add to self
            try:
                batch = db.batch()
                storyViewersRef = db.collection('Map').document(documentDict['publisherUid']) \
                    .collection('Coordinates').document('self') \
                    .collection('Viewers').document(storyId)

                batch.set(
                    storyViewersRef,
                    {
                        documentDict['viewerUid']: {
                            'viewerUsername': viewer_username,
                            'viewerFullName': viewer_fullname
                        }
                    },
                    merge=True
                )

                otherStoryRef = db.collection('Map').document(documentDict['viewerUid']) \
                    .collection('Coordinates').document('other')

                batch.update(
                    otherStoryRef,
                    {f'{storyId}.viewed': True}
                )

                batch.commit()

            except Exception as e:
                print(f'Error while updating story: {e}')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': f'document not in right format'
                })
                db.collection('StoryActionQueue').document(change.document.id).delete()

            db.collection('StoryActionQueue').document(change.document.id).delete()

        if change.type.name == 'REMOVED':
            print(f'Removed document {change.document.id}')
            print('\n')


def CheckingValidDocument(document_dict: dict) -> bool:
    try:
        if type(document_dict['viewerUid']) != str or type(document_dict['publisherUid']) != str or type(
                document_dict['storyId']) != str:
            return False
    except Exception as e:
        print(f'Error: {e}')

    return True

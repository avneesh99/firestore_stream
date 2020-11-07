from firebase_admin import firestore
from datetime import datetime
from django.utils import timezone
from core.sharing_story_functions.fan_out_functions import *
from core.models import ContentScoreModel


def SharingQueueOnSnapshot(col_snapshot, changes, read_time):
    db = firestore.client()
    for change in changes:
        if change.type.name == 'ADDED':
            print('\n')
            print(f'Received Document {change.document.id}')
            startTime: datetime = timezone.now()
            documentDict: dict = change.document.to_dict()

            if not CheckingValidDocument(documentDict=documentDict):
                print('not valid document')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': 'error in document validity'
                })
                db.collection('SharingQueue').document(change.document.id).delete()
                continue

            userDetailsDict = db.collection('UserDetails').document(documentDict['uid']).get().to_dict()
            try:
                publisherProfilePicture = userDetailsDict['profilePicture']
                publisherUsername = userDetailsDict['username']
            except Exception as e:
                print(f'user not found error {e}')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': f'userDetails not found for: {documentDict["uid"]}'
                })
                db.collection('SharingQueue').document(change.document.id).delete()
                continue

            contentDetailsDict = GettingReferencedContentDetailsDict(contentId=documentDict['contentId'])

            contentScoreObj: ContentScoreModel = ContentScoreModel.objects.filter(id=documentDict['contentId']).first()

            if 'pages' not in contentDetailsDict.keys() or contentScoreObj is None:
                print('pages missing')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': f'contentDetails not found for: {documentDict["contentId"]}'
                })
                db.collection('SharingQueue').document(change.document.id).delete()
                continue

            shareDict = {
                'storyId': change.document.id,
                'storyCreatedTime': documentDict['time'],

                'publisherUsername': publisherUsername,
                'publisherProfilePicture': publisherProfilePicture,
                'publisherUid': documentDict['uid'],

                'text': documentDict['text'],

                'referencedContentId': documentDict['contentId'],
                'category': contentScoreObj.category,  # We need original category for map
                'pageIndex': documentDict['pageIndex'],
                'referencedPage': contentDetailsDict['pages'][(documentDict['pageIndex'])],
                'referencedUsername': contentDetailsDict['user']['username'],
                'referencedProfilePicture': contentDetailsDict['user']['profilePicture'],
            }

            FanOut(publisherUid=documentDict['uid'], shareDict=shareDict)

            db.collection('SharingQueue').document(change.document.id).delete()
            print(f'Completed the process in {timezone.now() - startTime}')
            print('\n')


def GettingReferencedContentDetailsDict(contentId: str) -> dict:
    db = firestore.client()
    contentDocSnapshot = db.collection(u'Content').document(contentId).get()

    contentDetailsDict: dict = contentDocSnapshot.to_dict()

    if contentDetailsDict is None:
        return {}
    return contentDetailsDict


def CheckingValidDocument(documentDict: dict) -> bool:
    try:
        if type(documentDict['contentId']) != str:
            return False
    except Exception as e:
        print(f'Error in contentId: {e}')
        return False

    try:
        if type(documentDict['pageIndex']) != int:
            return False
    except Exception as e:
        print(f'Error in pageIndex: {e}')
        return False

    try:
        if type(documentDict['text']) != str:
            return False
    except Exception as e:
        print(f'Error in text: {e}')
        return False

    try:
        if type(documentDict['uid']) != str:
            return False
    except Exception as e:
        print(f'Error in uid: {e}')
        return False

    try:
        documentDict['time'].day
    except Exception as e:
        print(f'Error in time: {e}')
        return False

    return True

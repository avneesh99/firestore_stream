from datetime import datetime
from django.utils import timezone
from firebase_admin import firestore

from core.initialization_functions.add_to_AllUsers import AddToAllUsers
from core.initialization_functions.feed_functions import BuildAndSendFeed
from core.initialization_functions.map_functions import BuildAndSendMap


def OnboardingQueueOnSnapshot(colSnapshot, changes, readTime):
    db = firestore.client()
    for change in changes:
        if change.type.name == 'ADDED':
            print('\n')
            print(f'Received Document for onboarding {change.document.id}')
            documentDict: dict = change.document.to_dict()
            if not CheckingValidDocument(documentDict=documentDict, documentId=change.document.id):
                print(f'Error in the document {change.document.id}')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': 'error in document validity'
                })
                db.collection('OnboardingQueue').document(change.document.id).delete()
                continue

            mapStartTime: datetime = timezone.now()
            mapResult: bool = BuildAndSendMap(uid=documentDict['uid'])
            if mapResult:
                db.collection('UserDetails').document(documentDict['uid']).update({
                    'mapUnread': True
                })
                print(f'Done adding map in {timezone.now() - mapStartTime}')
            else:
                print('error adding map')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': 'error in adding map'
                })
                continue

            startTime: datetime = timezone.now()
            BuildAndSendFeed(userUid=documentDict['uid'],
                             rawFeedPreferenceDict=documentDict['InitialPreference'])

            db.collection('UserDetails').document(documentDict['uid']).update({
                'feedBuilt': True
            })
            print(f'Done building and sending feed in {timezone.now() - startTime}')

            addingToAllUsersResult = AddToAllUsers(uid=documentDict['uid'])

            if not addingToAllUsersResult:
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': 'error in adding to AllUsers collection'
                })
            else:
                db.collection('OnboardingQueue').document(change.document.id).delete()


def CheckingValidDocument(documentId: str, documentDict: dict) -> bool:
    try:
        if type(documentDict['InitialPreference']) != dict:
            return False
        for topic, preferenceValueList in documentDict['InitialPreference'].items():
            if type(topic) != str or type(preferenceValueList) != list:
                return False
            else:
                for preferenceValue in preferenceValueList:
                    if type(preferenceValue) != str:
                        return False
    except Exception as e:
        print(f'Error in initialPreference: {e}')
        return False

    try:
        if documentDict['uid'] != documentId:
            return False
    except Exception as e:
        print(f'Error in uid: {e}')
        return False

    try:
        documentDict['AddedToQueueTime'].day
    except Exception as e:
        print(f'Error in addToQueueTime: {e}')
        return False

    return True

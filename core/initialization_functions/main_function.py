from datetime import datetime

from django.utils import timezone

from core.initialization_functions.feed_functions import BuildAndSendFeed
from core.initialization_functions.map_functions import BuildAndSendMap


def OnboardingQueueOnSnapshot(colSnapshot, changes, readTime):
    for change in changes:
        if change.type.name == 'ADDED':
            print(f'Received Document for onboarding {change.document.id}')
            documentDict: dict = change.document.to_dict()

            if not CheckingValidDocument(documentDict=documentDict):
                print(f'Error in the document')
                continue
                # TODO: add what happens if document not valid

            FeedStartTime: datetime = datetime.utcnow()
            FeedResult = BuildAndSendFeed(uid=documentDict['uid'],
                                          initialFeedPreferenceDict=documentDict['InitialPreference'])
            if FeedResult:
                print(f'Done building and sending feed in {timezone.now() - FeedStartTime}')
            else:
                print('error building feed')
                # TODO send document to error collection
                continue

            mapStartTime: datetime = timezone.now()
            mapResult = BuildAndSendMap(uid=documentDict['uid'])
            if mapResult:
                print(f'Done adding map in {datetime.utcnow() - mapStartTime}')
            else:
                print('error adding map')
                # TODO send document to error collection


def CheckingValidDocument(documentDict: dict) -> bool:
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
        if type(documentDict['uid']) != str:
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

from firebase_admin import firestore
from random import uniform


def FanOut(publisherUid: str, shareDict: dict):
    print('Starting Fan out')
    followersUidList = GetFollowersUidList(publisherUid=publisherUid)

    # First send the story to the publisher map first
    # Then send it to their followers
    print(f'Starting for self')
    try:
        SendDataToUid(targetUid=publisherUid, shareDict=shareDict, selfStory=True)
        print(f'Done for self')
    except Exception as e:
        print(f'error in sending for uid: {e}')

    print('Starting for followers')
    for targetUid in followersUidList:
        try:
            SendDataToUid(targetUid=targetUid, shareDict=shareDict, selfStory=False)
        except Exception as e:
            print(f'error in sending for uid: {e}')
    print(f'Done for followers')


def GetFollowersUidList(publisherUid: str) -> list:
    db = firestore.client()
    followersUidDict = db.collection('SocialGraph').document(publisherUid) \
        .collection('View').document('followers').get().to_dict()

    if followersUidDict is None:
        return []
    else:
        return list(followersUidDict.keys())


def SendDataToUid(targetUid: str, shareDict: dict, selfStory: bool):
    db = firestore.client()
    mapColRef = db.collection('Map')
    mapDoc: dict = mapColRef.document(targetUid).get().to_dict()
    mappingDict: dict = mapDoc['mappingSubTopics']

    xCoord, yCoord = GetCoordinates(mappingDict=mappingDict, category=shareDict['category'])

    story_type = 'self' if selfStory else 'other'
    mapColRef.document(targetUid).collection('Coordinates').document(story_type).update({
        f'{shareDict["storyId"]}':
            {
                'xCoord': xCoord,
                'yCoord': yCoord,
                'viewed': False,
                'publisherUsername': shareDict['publisherUsername'],
                'publisherUid': shareDict['publisherUid'],
                'storyCreatedTime': shareDict['storyCreatedTime'],
                'text': shareDict['text'],
                'referencedPage': shareDict['referencedPage'],
                'referencedUsername': shareDict['referencedUsername'],
                'referencedProfilePicture': shareDict['referencedProfilePicture'],
                'referencedContentId': shareDict['referencedContentId'],
                'ownStory': selfStory
            }
    })

    db.collection('UserDetails').document(targetUid).update({
        'mapUnread': True
    })

    if selfStory:
        mapColRef.document(targetUid).collection('Coordinates') \
            .document('self').collection('Viewers') \
            .document(shareDict['storyId']).set({})


def GetCoordinates(mappingDict: dict, category: str) -> (float, float):

    try:
        modifiedCategory = {'music':'MusicGeneral', 'tech':'TechGeneral'}[category]
    except:
        modifiedCategory = category

    rangeDict = ReturnRange(category=modifiedCategory, mappingDict=mappingDict, rangeDict={})

    if type(rangeDict) != dict:
        rangeDict = {
            'minX': 0.67,
            'maxX': 1.0,
            'minY': 0.85,
            'maxY': 1.0
        }

    xCoord = uniform(rangeDict['minX'] + 0.1, rangeDict['maxX'] - 0.1)
    yCoord = uniform(rangeDict['minY'] + 0.1, rangeDict['maxY'] - 0.1)

    return xCoord, yCoord


def ReturnRange(category: str, mappingDict: dict, rangeDict: dict) -> dict:
    if category.lower() == 'home':
        return rangeDict

    for topic, subTopicDict in mappingDict.items():
        for subTopic, coordinateDict in subTopicDict.items():
            if subTopic.lower() == category.lower():
                newRangeDict = {
                    'minX': coordinateDict['x'],
                    'minY': coordinateDict['y'],
                    'maxX': coordinateDict['x'] + coordinateDict['width'],
                    'maxY': coordinateDict['y'] + coordinateDict['height']
                }

                if not rangeDict:
                    rangeDict = newRangeDict
                else:
                    height = coordinateDict['height']
                    width = coordinateDict['width']

                    rangeDict = {
                        'minX': newRangeDict['minX'] + rangeDict['minX'] * width,
                        'minY': newRangeDict['minY'] + rangeDict['minY'] * height,
                        'maxX': newRangeDict['minX'] + rangeDict['minX'] * width + width * (
                                rangeDict['maxX'] - rangeDict['minX']),
                        'maxY': newRangeDict['minY'] + rangeDict['minY'] * height + height * (
                                rangeDict['maxY'] - rangeDict['minY']),
                    }

                return ReturnRange(topic, mappingDict, rangeDict)

from firebase_admin import firestore
from random import uniform


def fan_out(publisher_uid: str, share_dict: dict) -> (bool, list):
    print('Starting Fan out')
    followers_uid_list = get_followers_uid_list(publisher_uid=publisher_uid)
    error_list = []

    print(f'Starting for self')
    try:
        send_data_to_uid(target_uid=publisher_uid, share_dict=share_dict, selfStory=True)
        print(f'Done for self')
    except Exception as e:
        print(f'error in sending for uid: {e}')

    for target_uid in followers_uid_list:
        print(f'Starting for {target_uid}')
        try:
            send_data_to_uid(target_uid=target_uid, share_dict=share_dict, selfStory=False)
            print(f'Done for {target_uid}')
        except Exception as e:
            print(f'error in sending for uid: {e}')

    return error_list


def send_data_to_uid(target_uid: str, share_dict: dict, selfStory: bool):
    db = firestore.client()
    map_col_ref = db.collection('Map')
    map_doc: dict = map_col_ref.document(target_uid).get().to_dict()
    mapping_dict: dict = map_doc['mappingSubTopics']

    xCoord, yCoord = get_coordinates(mapping_dict=mapping_dict, category=share_dict['category'])

    story_type = 'self' if selfStory else 'other'
    map_col_ref.document(target_uid).collection('Coordinates').document(story_type).update({
        f'{share_dict["storyId"]}':
            {
                'xCoord': xCoord,
                'yCoord': yCoord,
                'viewed': False,
                'publisherProfilePicture': share_dict['publisherProfilePicture'],
                'publisherUsername': share_dict['publisherUsername'],
                'publisherUid': share_dict['publisherUid'],
                'storyCreatedTime': share_dict['storyCreatedTime'],
                'text': share_dict['text'],
                'referencedPage': share_dict['referencedPage'],
                'referencedUsername': share_dict['referencedUsername'],
                'referencedProfilePicture': share_dict['referencedProfilePicture'],
                'referencedContentId': share_dict['referencedContentId'],
                'ownStory': selfStory
            }
    })

    if selfStory:
        map_col_ref.document(target_uid).collection('Coordinates') \
            .document('self').collection('Viewers') \
            .document(share_dict['storyId']).set({
                'viewersList': []
            })

    db.collection('UserDetails').document(target_uid).update({
        'mapUnread': True
    })


def get_followers_uid_list(publisher_uid: str) -> list:
    db = firestore.client()
    followers_uid_dict = db.collection('SocialGraph').document(publisher_uid) \
        .collection('View').document('followers').get().to_dict()

    if followers_uid_dict is None:
        return []
    else:
        return list(followers_uid_dict.keys())


def get_coordinates(mapping_dict: dict, category: str) -> (float, float):
    rangeDict = return_range(category=category, mapping_dict=mapping_dict, rangeDict={})

    print(rangeDict)

    xCoord = uniform(rangeDict['minX'] + 0.1, rangeDict['maxX'] - 0.1)
    yCoord = uniform(rangeDict['minY'] + 0.1, rangeDict['maxY'] - 0.1)

    return xCoord, yCoord


def return_range(category: str, mapping_dict: dict, rangeDict: dict) -> dict:
    if category.lower() == 'home':
        return rangeDict

    for topic, subTopicDict in mapping_dict.items():
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

                return return_range(topic, mapping_dict, rangeDict)

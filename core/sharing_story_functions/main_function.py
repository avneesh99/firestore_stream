from firebase_admin import firestore
from datetime import datetime
from core.sharing_story_functions.fan_out_functions import *


def sharing_queue_on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            print(f'Received Document {change.document.id}')
            start_time: datetime = datetime.utcnow()
            document_dict: dict = change.document.to_dict()

            if not checking_valid_document(document_dict=document_dict):
                # TODO: add what happens to document if it is not valid
                print('not valid document')
                continue

            db = firestore.client()
            userDetailsDict = db.collection('UserDetails').document(document_dict['uid']).get().to_dict()
            if ('profilePicture' not in userDetailsDict.keys()) or ('username' not in userDetailsDict.keys()):
                # TODO: add what happens if incorrect uid
                print('user not found')
                continue

            content_details_dict = getting_referenced_content_details_dict(content_id=document_dict['contentId'])

            if 'pages' not in content_details_dict.keys():
                # TODO: add what happens to document if it is not valid
                print('pages missing')
                continue

            share_dict = {
                'category': content_details_dict['category'],
                'pageIndex': document_dict['pageIndex'],
                'text': document_dict['text'],
                'referencedPage': content_details_dict['pages'][(document_dict['pageIndex'])],
                'referencedUsername': content_details_dict['user']['username'],
                'referencedProfilePicture': content_details_dict['user']['profilePicture'],
                'referencedContentId': document_dict['contentId'],
                'storyId': change.document.id,
                'storyCreatedTime': document_dict['time'],
                'publisherUsername': userDetailsDict['username'],
                'publisherProfilePicture': userDetailsDict['profilePicture'],
                'publisherUid': document_dict['uid']
            }

            error_list = fan_out(publisher_uid=document_dict['uid'], share_dict=share_dict)

            print(f'Completed the process in {datetime.utcnow() - start_time}')

        if change.type.name == 'REMOVED':
            f'Deleted Document {change.document.id}'


def getting_referenced_content_details_dict(content_id: str) -> dict:
    db = firestore.client()
    content_doc_snapshot = db.collection(u'content').document(content_id).get()

    content_details_dict: dict = content_doc_snapshot.to_dict()
    return content_details_dict


def checking_valid_document(document_dict: dict) -> bool:
    try:
        if type(document_dict['contentId']) != str:
            return False
    except Exception as e:
        print(f'Error in contentId {e}')
        return False

    try:
        if type(document_dict['pageIndex']) != int:
            return False
    except Exception as e:
        print(f'Error in contentId {e}')
        return False

    try:
        if type(document_dict['text']) != str:
            return False
    except Exception as e:
        print(f'Error in contentId {e}')
        return False

    try:
        if type(document_dict['uid']) != str:
            return False
    except Exception as e:
        print(f'Error in uid {e}')
        return False

    try:
        document_dict['time'].day
    except Exception as e:
        print(f'Error in time {e}')
        return False

    return True

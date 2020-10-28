from firebase_admin import firestore
from datetime import datetime


def BuildAndSendFeed(uid: str, initialFeedPreferenceDict: dict) -> bool:
    content_dict = get_content_dict()

    try:
        feed_list = build_feed(user_feed_preference_dict=initialFeedPreferenceDict, content_dict=content_dict)
    except Exception as e:
        print(f'Error in creating feed_list: {e}')
        return False

    try:
        send_feed(uid=uid, feed_list=feed_list)
    except Exception as e:
        print(f'Error in sending feed: {e}')
        return False

    try:
        edit_feed_preference_collection(uid=uid,
                                        initial_feed_preference_dict=initialFeedPreferenceDict)
    except Exception as e:
        print(f'Error in editing feed preference: {e}')
        return False

    return True


def get_content_dict():
    db = firestore.client()
    category_wise_content_col_ref = db.collection(u'CategoryWiseContent')
    content_dict = {}
    for doc_snapshot in category_wise_content_col_ref.stream():
        content_dict[doc_snapshot.id] = doc_snapshot.to_dict()['data']
    print('Done getting content_dict')
    return content_dict


def build_feed(user_feed_preference_dict: dict, content_dict: dict) -> list:
    feed_list = []
    category_order_list = []

    for category_name, preference_value in user_feed_preference_dict.items():
        if preference_value > 0:
            user_feed_preference_dict[category_name] = 2 ** (preference_value - 1)

    flag = True
    count_dict = {}
    while flag:
        flag = False
        for category_name, preference_value in user_feed_preference_dict.items():
            if category_name not in content_dict.keys():
                continue
            if preference_value > 0:
                flag = True
                category_order_list.append(category_name)
                user_feed_preference_dict[category_name] -= 1
            count_dict[category_name] = 0

    num_of_contents = 0
    counter = 0
    missed_counter = 0
    while num_of_contents < 100 and missed_counter < len(category_order_list):
        category_name = category_order_list[counter % len(category_order_list)]
        idx = count_dict[category_name]
        if idx < len(content_dict[category_name]):
            missed_counter = 0
            feed_list.append(content_dict[category_name][idx])
            count_dict[category_name] += 1
            num_of_contents += 1
        else:
            missed_counter += 1
        counter += 1

    return feed_list


def send_feed(feed_list, uid):
    db = firestore.client()

    i, feedNo = 0, 1
    while i < len(feed_list):
        db.collection('UserFeed').document(uid).collection('newsfeed').document(f'feed_{feedNo}').set({
            'feedList': feed_list[i:i + 10]
        })
        feedNo += 1
        i += 10

    db.collection('UserFeed').document(uid).set({
        'feedCount': feedNo-1
    })


def edit_feed_preference_collection(uid: str, initial_feed_preference_dict: dict):
    db = firestore.client()

    db.collection('FeedPreference').document(uid).set({
        'InitialPreference': initial_feed_preference_dict,
        'LastUpdated': datetime.utcnow()
    })

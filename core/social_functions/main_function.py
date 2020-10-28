from firebase_admin import firestore


def following_queue_on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name in ['ADDED', 'MODIFIED']:
            print(f'Received Document for following request: {change.document.id}')
            document_dict = change.document.to_dict()

            if not checking_valid_document(document_dict=document_dict):
                # TODO: what to do if error
                print('not in right format')
                continue

            db = firestore.client()

            follower_uid = document_dict['userUid']
            following_uid = document_dict['followingUserUid']

            follower_user_details_dict = db.collection('UserDetails').document(follower_uid).get().to_dict()
            try:
                followerFullName = follower_user_details_dict['fullName']
                followerUsername = follower_user_details_dict['username']
            except Exception as e:
                print(f'Error in getting follower user details: {e}')
                continue

            following_user_details_dict = db.collection('UserDetails').document(following_uid).get().to_dict()
            try:
                followingFullName = following_user_details_dict['fullName']
                followingUsername = following_user_details_dict['username']
            except Exception as e:
                print(f'Error in getting following user details: {e}')
                continue

            if document_dict['follow']:
                # Adding to View
                db.collection('SocialGraph').document(following_uid) \
                    .collection('View').document('followers').set({
                        f'{follower_uid}': {'fullName': followerFullName, 'username': followerUsername}
                    })

                db.collection('SocialGraph').document(follower_uid) \
                    .collection('View').document('following').set({
                        f'{following_uid}': {'fullName': followingFullName, 'username': followingUsername}
                    })
                # Adding to Search
                db.collection('SocialGraph').document(follower_uid) \
                    .collection('Search').document('following') \
                    .collection('Values').document(following_uid).set({
                        'fullName': followingFullName,
                        'username': followingUsername,
                        'searchKeywordsList': getSearchKeywordsList(username=followingUsername,
                                                                    fullName=followingFullName),
                    })

            else:
                # Removing from View
                db.collection('SocialGraph').document(following_uid) \
                    .collection('View').document('followers').update({
                        f'{follower_uid}': firestore.DELETE_FIELD
                    })

                db.collection('SocialGraph').document(follower_uid) \
                    .collection('View').document('following').update({
                        f'{following_uid}': firestore.DELETE_FIELD
                    })

                # Removing from Search
                db.collection('SocialGraph').document(follower_uid) \
                    .collection('Search').document('following') \
                    .collection('Values').document(following_uid).delete()

            print(f"Done adding to social_graph")

            db.collection('FollowingQueue').document(change.document.id).delete()

        if change.type.name == 'REMOVED':
            print(f'Deleted document: {change.document.id}')


def checking_valid_document(document_dict: dict) -> bool:
    try:
        if type(document_dict['follow']) != bool:
            return False
    except Exception as e:
        print(f'Error in follow field: {e}')
        return False

    try:
        if type(document_dict['followingUserUid']) != str or type(document_dict['userUid']) != str:
            return False
    except Exception as e:
        print(f'Error in other fields {e}')
        return False

    return True


def getSearchKeywordsList(fullName: str, username: str) -> list:
    searchKeywordsList = []
    searchKeywordsList.extend(fullName.lower().split(' '))
    searchKeywordsList.append(''.join(fullName.lower().split(' ')))
    searchKeywordsList.append(''.join(fullName.lower().split(' ')[::-1]))
    searchKeywordsList.extend(username.lower().split(' '))

    return searchKeywordsList

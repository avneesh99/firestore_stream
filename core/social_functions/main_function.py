from firebase_admin import firestore


def FollowingQueueOnSnapshot(col_snapshot, changes, read_time):
    db = firestore.client()
    for change in changes:
        if change.type.name in ['ADDED', 'MODIFIED']:
            print('\n')
            print(f'Received Document for following request: {change.document.id}')
            documentDict = change.document.to_dict()

            if not CheckingValidDocument(documentDict=documentDict):
                print('not in right format')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': 'following document not in right format'
                })
                db.collection('FollowingQueue').document(change.document.id).delete()
                continue

            followerUid = documentDict['userUid']
            followingUid = documentDict['followingUserUid']

            try:
                followerUserDetailsDict = db.collection('UserDetails').document(followerUid).get().to_dict()
                followerFullName = followerUserDetailsDict['fullName']
                followerUsername = followerUserDetailsDict['username']

                followingUserDetailsDict = db.collection('UserDetails').document(followingUid).get().to_dict()
                followingFullName = followingUserDetailsDict['fullName']
                followingUsername = followingUserDetailsDict['username']
            except Exception as e:
                print(f'Error in getting following user details: {e}')
                db.collection('Errors').document(change.document.id).set({
                    'documentDict': documentDict,
                    'error': f'error in getting following user details of {followingUid}'
                })
                db.collection('FollowingQueue').document(change.document.id).delete()
                continue

            batch = db.batch()
            if documentDict['follow']:
                # Adding to View
                followersRef = db.collection('SocialGraph').document(followingUid) \
                    .collection('View').document('followers')

                batch.set(
                    followersRef,
                    {
                        followerUid: {'fullName': followerFullName, 'username': followerUsername}
                    },
                    merge=True
                )

                followingRef = db.collection('SocialGraph').document(followerUid) \
                    .collection('View').document('following')

                batch.set(
                    followingRef,
                    {
                        followingUid: {'fullName': followingFullName, 'username': followingUsername}
                    },
                    merge=True
                )

                batch.commit()

            else:
                # Removing from View
                followersRef = db.collection('SocialGraph').document(followingUid) \
                    .collection('View').document('followers')

                batch.update(
                    followersRef,
                    {f'{followerUid}': firestore.DELETE_FIELD}
                )

                followingRef = db.collection('SocialGraph').document(followerUid) \
                    .collection('View').document('following')

                batch.update(
                    followingRef,
                    {f'{followingUid}': firestore.DELETE_FIELD}
                )

                batch.commit()

            print(f"Done adding to social_graph")

            db.collection('FollowingQueue').document(change.document.id).delete()

        if change.type.name == 'REMOVED':
            print(f'Deleted document: {change.document.id}')
            print('\n')


def CheckingValidDocument(documentDict: dict) -> bool:
    try:
        if type(documentDict['follow']) != bool:
            return False
    except Exception as e:
        print(f'Error in follow field: {e}')
        return False

    try:
        if type(documentDict['followingUserUid']) != str or type(documentDict['userUid']) != str:
            return False
    except Exception as e:
        print(f'Error in other fields {e}')
        return False

    return True

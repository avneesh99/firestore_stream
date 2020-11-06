from typing import List

from firebase_admin import firestore


def AddToAllUsers(uid: str) -> bool:
    db = firestore.client()
    try:
        userDetailsDict = db.collection('UserDetails').document(uid).get().to_dict()

        if userDetailsDict is None:
            print(f'failed to get user details for uid: {uid}')
            return False

        fullName = userDetailsDict['fullName']
        username = userDetailsDict['username']

        db.collection('AllUsers').document(uid).set({
            'fullName': fullName,
            'username': username,
            'searchKeywordsList': firestore.ArrayUnion(getSearchKeywordsList(fullName=fullName, username=username))
        })

        return True

    except Exception as e:
        print(f'Error while adding {uid} to AllUsers: {e}')
        return False


def getSearchKeywordsList(fullName: str, username: str) -> list[str]:
    searchKeywordsList: list[str] = []
    searchKeywordsList.extend(fullName.lower().split(' '))
    searchKeywordsList.append(''.join(fullName.lower().split(' ')))
    searchKeywordsList.append(''.join(fullName.lower().split(' ')[::-1]))
    searchKeywordsList.extend(username.lower().split(' '))

    return searchKeywordsList

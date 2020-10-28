from firebase_admin import firestore


def BuildAndSendMap(uid: str) -> bool:
    mappingSubTopics = {
                           'Home': {
                               'Finance': {'x': 0, 'y': 0, 'height': 0.25, 'width': 0.5},
                               'India': {'x': 0.5, 'y': 0, 'height': 0.25, 'width': 0.5},

                               'Hollywood': {'x': 0, 'y': 0.25, 'height': 0.15, 'width': 0.33},
                               'Music': {'x': 0.33, 'y': 0.25, 'height': 0.15, 'width': 0.34},
                               'Bollywood': {'x': 0.67, 'y': 0.25, 'height': 0.15, 'width': 0.33},

                               'Sports': {'x': 0, 'y': 0.4, 'height': 0.2, 'width': 0.75},
                               'Gaming': {'x': 0.75, 'y': 0.4, 'height': 0.2, 'width': 0.25},

                               'Tech': {'x': 0.0, 'y': 0.6, 'height': 0.2, 'width': 0.5},
                               'Sample': {'x': 0.5, 'y': 0.6, 'height': 0.2, 'width': 0.5},

                               'Science': {'x': 0.0, 'y': 0.8, 'height': 0.2, 'width': 0.25},
                               'World': {'x': 0.25, 'y': 0.8, 'height': 0.2, 'width': 0.75},
                           },
                           'Sports': {
                               'Cricket': {'x': 0.0, 'y': 0.0, 'height': 0.5, 'width': 0.75},
                               'F1': {'x': 0.75, 'y': 0.0, 'height': 0.5, 'width': 0.25},

                               'Tennis': {'x': 0.0, 'y': 0.5, 'height': 0.5, 'width': 0.25},
                               'Football': {'x': 0.25, 'y': 0.5, 'height': 0.5, 'width': 0.75},
                           }
                       }

    try:
        db = firestore.client()
        db.collection('Map').document(uid).set({
            'mappingSubTopics': mappingSubTopics
        })
        db.collection('Map').document(uid).collection('Coordinates').document('other').set({})
        db.collection('Map').document(uid).collection('Coordinates').document('self').set({})
    except Exception as e:
        print(f'Error in adding map: {e}')
        return False

    return True

import os

from django.core.management.base import BaseCommand
from django.utils import timezone

import firebase_admin
from firebase_admin import credentials, firestore
from time import sleep

from core.initialization_functions.main import OnboardingQueueOnSnapshot
from core.sharing_story_functions.main_function import SharingQueueOnSnapshot
from core.social_functions.main_function import FollowingQueueOnSnapshot
from core.story_action_functions.main_function import story_action_queue_on_snapshot


class Command(BaseCommand):
    def handle(self, *args, **options):
        firestore_cred_data = {
            'auth_provider_x509_cert_url': os.environ['auth_provider_x509_cert_url'],
            'auth_uri': os.environ['auth_uri'],
            'client_email': os.environ['client_email'],
            'client_id': os.environ['client_id'],
            'client_x509_cert_url': os.environ['client_x509_cert_url'],
            'DATABASE_URL': os.environ['DATABASE_URL'],
            'private_key': os.environ['private_key'].replace('\\n', '\n'),
            'private_key_id': os.environ['private_key_id'],
            'project_id': os.environ['project_id'],
            'token_uri': os.environ['token_uri'],
            'type': os.environ['type']
        }
        print(firestore_cred_data)
        print('Starting script.py........................')
        print('\n')
        print('\n')

        cred = credentials.Certificate(firestore_cred_data)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        print('Connection Initialised')

        sharingQueueColRef = db.collection(u'SharingQueue')
        sharingQueueColRef.on_snapshot(SharingQueueOnSnapshot)

        onboardingQueueColRef = db.collection(u'OnboardingQueue')
        onboardingQueueColRef.on_snapshot(OnboardingQueueOnSnapshot)

        followingQueueColRef = db.collection(u'FollowingQueue')
        followingQueueColRef.on_snapshot(FollowingQueueOnSnapshot)

        story_action_queue_col_ref = db.collection(u'StoryActionQueue')
        story_action_queue_col_ref.on_snapshot(story_action_queue_on_snapshot)

        while True:
            print(f'processing @ {timezone.now()}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            sleep(300)

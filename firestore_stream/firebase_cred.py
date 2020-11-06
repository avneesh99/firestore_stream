import os
firestore_cred_data = {
    'auth_provider_x509_cert_url': os.environ['auth_provider_x509_cert_url'],
    'auth_uri': os.environ['auth_uri'],
    'client_email': os.environ['client_email'],
    'client_id': os.environ['client_id'],
    'client_x509_cert_url': os.environ['client_x509_cert_url'],
    'DATABASE_URL': os.environ['DATABASE_URL'],
    'private_key': os.environ['private_key'],
    'private_key_id': os.environ['private_key_id'],
    'project_id': os.environ['project_id'],
    'token_uri': os.environ['token_uri'],
    'type': os.environ['type']
}

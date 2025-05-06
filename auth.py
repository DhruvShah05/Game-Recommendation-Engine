from google_auth_oauthlib.flow import InstalledAppFlow

def authenticate_user():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email']
    )
    creds = flow.run_local_server(host='127.0.0.1', port=9080, open_browser=True)
    
    from google.oauth2 import id_token
    from google.auth.transport import requests

    idinfo = id_token.verify_oauth2_token(
        creds.id_token,
        requests.Request(),
        audience=None
    )
    return idinfo['email']

from authlib.integrations.starlette_client import OAuth
from config import get_settings

settings = get_settings()
oauth = OAuth()
oauth.register(
    name="auth0",
    client_id=settings.OAUTH_CLIENT_ID,
    client_secret=settings.OAUTH_CLIENT_SECRET,
    # authorize_url=f"https://{settings.OAUTH_DOMAIN}/authorize",
    # access_token_url=f"https://{settings.OAUTH_DOMAIN}/oauth/token",
    server_metadata_url=f'https://{settings.OAUTH_DOMAIN}/.well-known/openid-configuration',
    client_kwargs={"scope": "openid profile email"},
)
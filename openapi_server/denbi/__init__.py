import os

from keystoneauth1 import session
from keystoneauth1.identity import v3

def create_session(app_name="denbi", app_version="1.0"):
    auth = v3.Password(username=os.environ["OS_USERNAME"],
                       password=os.environ["OS_PASSWORD"],
                       auth_url=os.environ["OS_AUTH_URL"],
                       project_name=os.environ["OS_PROJECT_NAME"],
                       user_domain_name=os.environ["OS_USER_DOMAIN_NAME"],
                       project_domain_name=os.environ["OS_USER_DOMAIN_NAME"])
    return session.Session(auth=auth, app_name=app_name, app_version=app_version)
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
from pathlib import Path

from dotenv import load_dotenv


_CONFIG_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=_CONFIG_DIR / '.env')


class BaseConfig(object):

    # Can be set to 'MasterUser' or 'ServicePrincipal'
    AUTHENTICATION_MODE = os.getenv('AUTHENTICATION_MODE', 'ServicePrincipal')

    # Workspace Id in which the report is present
    WORKSPACE_ID = os.getenv('WORKSPACE_ID', '')

    # Report Id for which Embed token needs to be generated
    REPORT_ID = os.getenv('REPORT_ID', '')

    # Id of the Azure tenant in which AAD app and Power BI report is hosted. Required only for ServicePrincipal authentication mode.
    TENANT_ID = os.getenv('TENANT_ID', '')

    # Client Id (Application Id) of the AAD app
    CLIENT_ID = os.getenv('CLIENT_ID', '')

    # Client Secret (App Secret) of the AAD app. Required only for ServicePrincipal authentication mode.
    CLIENT_SECRET = os.getenv('CLIENT_SECRET', '')

    # Scope Base of AAD app. Use the below configuration to use all the permissions provided in the AAD app through Azure portal.
    SCOPE_BASE = [scope.strip() for scope in os.getenv('SCOPE_BASE', 'https://analysis.windows.net/powerbi/api/.default').split(',') if scope.strip()]

    # URL used for initiating authorization request
    AUTHORITY_URL = os.getenv('AUTHORITY_URL', 'https://login.microsoftonline.com/organizations')

    # Master user email address. Required only for MasterUser authentication mode.
    POWER_BI_USER = os.getenv('POWER_BI_USER', '')

    # Master user email password. Required only for MasterUser authentication mode.
    POWER_BI_PASS = os.getenv('POWER_BI_PASS', '')

    # OIDC settings (derive from core AAD values to avoid duplication)
    OIDC_REDIRECT_URI = os.getenv('OIDC_REDIRECT_URI', 'http://localhost:8000/auth/callback')
    # Use tenant authority without version segment; endpoints add "/oauth2/v2.0/..."
    OIDC_AUTHORITY = os.getenv('OIDC_AUTHORITY', f'https://login.microsoftonline.com/{TENANT_ID}')
    OIDC_SCOPES = [s.strip() for s in os.getenv('OIDC_SCOPES', 'openid,profile,email,offline_access').split(',') if s.strip()]

    # Session settings
    SESSION_SECRET = os.getenv('SESSION_SECRET', '')
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'filesystem')

    # Where to go after Azure AD logout completes
    POST_LOGOUT_REDIRECT_URI = os.getenv('POST_LOGOUT_REDIRECT_URI', 'http://localhost:8000/')

    # RLS identity behavior: 'auto' (use when required), 'on' (force), 'off' (never)
    RLS_MODE = os.getenv('RLS_MODE', 'auto').lower()
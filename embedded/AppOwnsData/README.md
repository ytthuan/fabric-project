# Power BI Embedded – App Owns Data (Flask)

This sample shows how to embed a Power BI report in a multitenant web experience using the App-Owns-Data pattern. The project uses Flask, Authlib, and the Power BI REST APIs to acquire access tokens and render an embedded report.

## Prerequisites

- Python 3.10 or later installed and available on your `PATH`
- Power BI Pro (or Premium Per User) account with access to the desired report
- A Power BI workspace containing the report you want to embed
- An Azure AD application registration configured for either Service Principal or Master User authentication
- (Optional) `virtualenv` or another environment tool to isolate dependencies

## Project Structure

- `app.py` – Flask entry point hosting OAuth flows and serving the embedded page
- `config.py` – Loads configuration values from environment variables / `.env`
- `services/` – Helpers for authenticating against Azure AD and generating embed tokens
- `templates/index.html` & `static/` – UI assets used to render the embedded report

## 1. Clone and Create a Virtual Environment

```bash
git clone https://github.com/ytthuan/fabric-project.git
cd fabric-project/embedded/AppOwnsData
python3 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate with:

```powershell
.venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Secrets and IDs

`config.py` reads settings from environment variables (preferably through a `.env` file located beside `config.py`). Create `embedded/AppOwnsData/.env` with the values that match your Azure resources.

```
AUTHENTICATION_MODE=ServicePrincipal  # or MasterUser
WORKSPACE_ID=00000000-0000-0000-0000-000000000000
REPORT_ID=00000000-0000-0000-0000-000000000000
TENANT_ID=00000000-0000-0000-0000-000000000000
CLIENT_ID=00000000-0000-0000-0000-000000000000
CLIENT_SECRET=your-client-secret
POWER_BI_USER= # Required only for MasterUser mode
POWER_BI_PASS= # Required only for MasterUser mode
SCOPE_BASE=https://analysis.windows.net/powerbi/api/.default
OIDC_REDIRECT_URI=http://localhost:8000/auth/callback
OIDC_SCOPES=openid,profile,email,offline_access
SESSION_SECRET=replace-with-random-32-byte-value
SESSION_TYPE=filesystem
POST_LOGOUT_REDIRECT_URI=http://localhost:8000/
RLS_MODE=auto
```

Key configuration notes:

- **Service Principal mode** requires delegating the workspace to the Azure AD app and granting `Tenant.Read.All` + Power BI API permissions.
- **Master User mode** signs in with a licensed Power BI user. Populate `POWER_BI_USER` and `POWER_BI_PASS` and ensure MFA is disabled or satisfied via modern auth.
- Rotate secrets securely (consider Azure Key Vault) before deploying outside development.

## 4. Register an Azure AD Application

1. Create an app registration in Azure portal.
2. Add a client secret (for Service Principal) or enable delegated permissions (for Master User).
3. Expose the API permissions `Power BI Service → Workspace.Read.All` and `Report.Read.All`.
4. Add a web redirect URI matching `OIDC_REDIRECT_URI` (default `http://localhost:8000/auth/callback`).
5. Grant admin consent for the required permissions.
6. Add the service principal as an Admin or Member of the Power BI workspace if using Service Principal mode.

## 5. Prepare the Power BI Report

1. Publish the report to the workspace referenced by `WORKSPACE_ID`.
2. Verify the report `REPORT_ID` matches the published artifact (check in the Power BI portal URL under `?reportId=`).
3. Ensure dataset permissions align with any RLS settings you plan to enforce (`RLS_MODE`).

## 6. Run the Flask Application Locally

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=localhost --port=8000
```

On Windows CMD:

```cmd
set FLASK_APP=app.py
set FLASK_ENV=development
flask run --host=localhost --port=8000
```

Visit `http://localhost:8000` and complete the Azure AD sign-in to render the embedded report.

## 7. Troubleshooting

- **401 / 403 errors when fetching embed info**: Confirm the app registration has the correct API permissions and is added to the workspace.
- **Invalid OAuth state / nonce**: Clear browser cookies or restart the Flask server to reset the session secrets.
- **Missing configuration**: The helper `Utils.check_config` validates required values; check server logs for precise missing fields.
- **Token acquisition failures**: Ensure `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET` (or `POWER_BI_USER` / `POWER_BI_PASS`) are correct and not expired.

## 8. Next Steps

- Replace in-memory secrets with a secure store such as Azure Key Vault.
- Containerize the app or deploy to Azure App Service once configuration is stable.
- Add automated tests around token acquisition and embed token generation before production use.



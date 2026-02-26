/**
 * Azure AD MSAL.js authentication service — Story 5.1, Task 3.2
 *
 * AC #4: MSAL.js v2 for seamless SSO token acquisition.
 * Reads config from environment variables injected at build time.
 */
import { PublicClientApplication, InteractionRequiredAuthError } from '@azure/msal-browser'

const msalConfig = {
  auth: {
    clientId:    import.meta.env.VITE_AZURE_AD_CLIENT_ID  || '',
    authority:   `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_AD_TENANT_ID || ''}`,
    redirectUri: import.meta.env.VITE_REDIRECT_URI || window.location.origin,
  },
  cache: {
    cacheLocation:       'sessionStorage',
    storeAuthStateInCookie: false,
  },
}

const loginRequest = {
  scopes: [`api://${import.meta.env.VITE_AZURE_AD_CLIENT_ID || ''}/.default`],
}

let _msalInstance = null

/** Return (or create) the singleton MSAL PublicClientApplication. */
export function getMsalInstance() {
  if (!_msalInstance) {
    _msalInstance = new PublicClientApplication(msalConfig)
  }
  return _msalInstance
}

/** Reset MSAL instance (used in tests). */
export function _resetMsalInstance() {
  _msalInstance = null
}

/**
 * Acquire a Bearer token silently; fall back to interaction if needed.
 * AC #4: Seamless SSO — silent acquisition first.
 *
 * @returns {Promise<string>} Access token
 */
export async function acquireToken() {
  const msal = getMsalInstance()
  await msal.initialize()

  const accounts = msal.getAllAccounts()
  if (!accounts.length) {
    await msal.loginRedirect(loginRequest)
    return ''
  }

  const silentRequest = { ...loginRequest, account: accounts[0] }

  try {
    const response = await msal.acquireTokenSilent(silentRequest)
    return response.accessToken
  } catch (err) {
    if (err instanceof InteractionRequiredAuthError) {
      await msal.acquireTokenRedirect(silentRequest)
    }
    throw err
  }
}

/**
 * Return the currently signed-in account, or null.
 */
export function getCurrentAccount() {
  const msal = getMsalInstance()
  const accounts = msal.getAllAccounts()
  return accounts[0] ?? null
}

/**
 * Sign out the current user.
 */
export async function signOut() {
  const msal = getMsalInstance()
  await msal.initialize()
  const account = getCurrentAccount()
  await msal.logoutRedirect({ account })
}

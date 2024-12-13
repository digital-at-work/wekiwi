import { setContext, getContext } from 'svelte';

import { env } from '$env/dynamic/public';
const PUBLIC_FRONTEND_URL = env.PUBLIC_FRONTEND_URL;
const PUBLIC_CMS_URL = env.PUBLIC_CMS_URL;

import { route } from '$lib/ROUTES'

import type { CustomDirectusTypes } from './directus.types'
import { createDirectus, rest, authentication } from "@directus/sdk";


// IMPORTANT: never use getDirectusInstance() directly in the client
function getDirectusInstance(authType: 'json' | 'session', token: string | null = null, fetchInstance: typeof fetch | undefined, URL: string = PUBLIC_CMS_URL) {
  const options = fetchInstance ? { globals: { fetch: fetchInstance } } : {};

  const directus = createDirectus<CustomDirectusTypes>(URL, options)
    .with(authType === 'session' ? authentication('session') : authentication('json')) //Not sure { credentials: 'include' } is needed here
    .with(rest()); //Not sure { credentials: 'include' } is needed here

  if (token) directus.setToken(token);

  return directus;
}

// Server: export the server object directly
export default getDirectusInstance;

// Client: export getter and setter functions for the directus client
const first_key = Symbol();
export function setDirectusClient(authType: 'session', fetchInstance: typeof fetch) {
  setContext(first_key, getDirectusInstance(authType, null, fetchInstance));
}

export function getDirectusClient() {
  return getContext(first_key) as ReturnType<typeof getDirectusInstance>;
}

// Client: export getter and setter functions for the directus client proxy
const second_key = Symbol();
export function setDirectusClientProxy(fetchInstance: typeof fetch) {
  setContext(second_key, getDirectusInstance('json', null, fetchInstance, route('cms_proxy',  {cms_slug: ""})));
}

export function getDirectusClientProxy() {
  return getContext(second_key) as ReturnType<typeof getDirectusInstance>;
}

export const constructCookieOpts = (
  age: number,
  path: string = '/',
  sameSite: "strict" | "lax" | "none" | undefined = 'strict'
) => {
  return {
    'domain': PUBLIC_FRONTEND_URL, // The cookie is only sent to requests under this domain
    'path': path, // The cookie is only sent to requests under this path
    'httpOnly': true, // Server-side only cookie, inaccessible via `document.cookie`
    'sameSite': process.env.NODE_ENV === 'production' ? sameSite : 'none', // Set to `none` in production to allow for cross-site cookies
    'secure': process.env.NODE_ENV === 'production', // Sent over HTTPS only in production
    'maxAge': age // Set cookie to expire after "age" seconds
  };
};
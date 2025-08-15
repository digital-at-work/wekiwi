import { redirect, error } from '@sveltejs/kit';
import { sequence } from '@sveltejs/kit/hooks';

import type { Handle, Cookies } from '@sveltejs/kit';

import proxyHandle from '$lib/proxy.js'

import { constructCookieOpts } from '$lib/directus/directus';
import getDirectusInstance from '$lib/directus/directus';

import jwt from 'jsonwebtoken';
import type { JwtPayload } from 'jsonwebtoken';

import { route } from '$lib/ROUTES';

import { env as publicEnv } from '$env/dynamic/public';
import { env as privateEnv } from '$env/dynamic/private';

const PUBLIC_CMS_URL = publicEnv.PUBLIC_CMS_URL;
const PUBLIC_ALEPH_CHAT_URL = publicEnv.PUBLIC_ALEPH_CHAT_URL;
const PUBLIC_AI_SERVER_URL = publicEnv.PUBLIC_AI_SERVER_URL;
const PUBLIC_AISERVER_PORT = publicEnv.PUBLIC_AI_SERVER_PORT;

const ALEPH_ALPHA_TOKEN = privateEnv.ALEPH_ALPHA_TOKEN;
const AI_API_KEY = privateEnv.AI_API_KEY;
const PRIVATE_OLLAMA_URL = privateEnv.PRIVATE_OLLAMA_URL ?? 'http://185.64.113.27:8080';  // Fallback for type safety

const TOKEN_EXPIRATION_BUFFER = 0;

// exchange the refresh token for an access token
async function refreshAccessToken(cookies: Cookies) {
	let res = await fetch(PUBLIC_CMS_URL + "/auth/refresh", {
		method: "POST",
		mode: "cors",
		headers: {
			Accept: "application/json, text/plain, */*",
			"Content-Type": "application/json",
		},
		body: JSON.stringify({ refresh_token: cookies.get('refresh_token') }),
	});

	if (res.status >= 300) {
		cookies.delete('refresh_token', { path: '/' });
		cookies.delete('access_token', { path: '/' });
		error(500, "Refresh Token Status != 200");
	}
	let data = (await res.json()).data;

	cookies.set("refresh_token", data.refresh_token, constructCookieOpts(60 * 60 * 24 * 30, "/"));
	cookies.set("access_token", data.access_token, constructCookieOpts(Math.floor(data.expires / 1000), "/"));
}

function isTokenExpired(jwtPayload: JwtPayload) {
	return (jwtPayload?.exp || 0) < Math.floor(Date.now() / 1000) + TOKEN_EXPIRATION_BUFFER;
}


function isPublicRoute(url: string): boolean {
	// check for public routes: returns true if the route is public
	return (['/sign-up', '/sign-in', '/password', '/imprint/termsofuse', '/imprint/privacypolicy'].some(part => url.includes(part)) || url === '/');
}


const svelteHandle: Handle = async ({ event, resolve }) => {
	const { cookies, url, locals, fetch } = event;

	console.log('[HOOKS] url: ', url.pathname)
	
	if (cookies.get('access_token') || cookies.get('refresh_token')) {
		let jwtPayload = cookies.get('access_token') ? jwt.decode(cookies.get('access_token') || "") : false;

		//check if token is expired and renew it if necessary
		if (isTokenExpired(jwtPayload as JwtPayload) || !cookies.get('access_token')) {
			try {
				await refreshAccessToken(cookies);
				jwtPayload = cookies.get('access_token') ? jwt.decode(cookies.get('access_token') || "") : false;
			} catch (err) {
				cookies.delete('refresh_token', { path: '/' });
				cookies.delete('access_token', { path: '/' });

				console.error('Fehler bei der JWT Aktualisierung. Refreshtoken abgelaufen?');

				redirect(308, route('/auth/sign-in'));
			}
		}

		if (jwtPayload && typeof jwtPayload === 'object') {
			locals.user = {
				id: jwtPayload?.id,
				token: cookies.get('access_token') || "",
				circles: JSON.parse(cookies.get('circles') || '[]'),
			};
		}
	}

	// Redirect to login, if user is not logged in and accessing non public routes and the route it not the sign-in/out/up route
	if (!locals.user && !isPublicRoute(url.pathname) && !url.pathname.match(/auth\/sign-(in|out|up)/)) {
		console.log('[HOOKS] non- public route, user not logged in, redirecting to sign-in')
		// Do not redirect if the user has a share_key and wants to access a single content
		if (!(url.pathname.match(/\/app\d+/) && url.searchParams.get('share_key'))) {
			redirect(307, route("/auth/sign-in", { redirectedFrom: encodeURIComponent(url.pathname) }));
		}
	}

	const circlesRequested = url.searchParams.get('circles');

	// If user accesses circles, check if they are contained in 'circles' cookie, if not, remove them from the request
	if (circlesRequested && !!locals.user?.circles.length) {
		const userCircleIds = new Set(locals.user?.circles.map(c => c.id));
		const circlesRequestedArray = JSON.parse(circlesRequested);
		const validCircles = circlesRequestedArray.filter((circleId: string) => userCircleIds.has(circleId));

		if (validCircles.length !== circlesRequestedArray.length) {
			const searchParams = new URLSearchParams(url.search);
			searchParams.set('circles', JSON.stringify(validCircles));
			console.debug('[Hooks] redirect + remove invalid circles')
			redirect(307, `${url.pathname}?${searchParams.toString()}`);
		}
	}

	// set directus instance 
	event.locals.directusInstance = getDirectusInstance('json', cookies.get('access_token') || null, fetch);


	// this is needed so that the response headers from SvelteKit do include the correct header to allow the browser to parse json requests
	return await resolve(event, {
		filterSerializedResponseHeaders: (key) => {
			return key.toLowerCase() === 'content-type'
		}
	});
};

export const handle = sequence(
	// Can be used to make authenticated request from the client and avoid CORS issues
	// The cmsproxy route can be used via kitroutes like this: route('cms_proxy',  {cms_slug: "/XXX"})
	// (making a fetch request to https://www.wekiwi.de:3000/cmsproxy/XXX will be proxied to PUBLIC_CMS_URL/XXX)
	// proxy handle expects {first path of the route (used to identify proxy): [the route of the proxy, a token (optional)]}
	proxyHandle({
		'/aiproxy': [`${PUBLIC_AI_SERVER_URL}:${PUBLIC_AISERVER_PORT}`, AI_API_KEY],
		'/cmsproxy': [PUBLIC_CMS_URL],
		'/aleph_alpha_proxy': [PUBLIC_ALEPH_CHAT_URL, ALEPH_ALPHA_TOKEN],
		'/ollama_proxy': [PRIVATE_OLLAMA_URL]
	},
		{ changeOrigin: true, debug: false }
	),
	svelteHandle,
);




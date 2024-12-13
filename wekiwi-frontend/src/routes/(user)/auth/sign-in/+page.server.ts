import type { PageServerLoad, Actions } from './$types';
import { fail } from '@sveltejs/kit';

import { setError, superValidate } from 'sveltekit-superforms';
import { signInSchema } from '$lib/config/zod-schemas';
import { zod } from 'sveltekit-superforms/adapters';

import { redirect } from 'sveltekit-flash-message/server';

import { route } from '$lib/ROUTES'

import { readItems } from "@directus/sdk";


export const load: PageServerLoad = async (event) => {

	if (event.locals.user) {

		const redirectFrom = decodeURIComponent(event.url.searchParams.get('redirectedFrom') || '')
		if (redirectFrom) console.debug("(user)/auth/sign-in/+page.server.ts: page was called from: ", redirectFrom, "redirecting back");

		// redirect logged in users to the main page or page they were redirected from
		redirect(307, redirectFrom || route('/'));
	}

	return {
		form: await superValidate(event, zod(signInSchema))
	};
};

export const actions = {
	default: async (event) => {
		const { locals, cookies } = event;
		const form = await superValidate(event, zod(signInSchema));

		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		try {
			// Login the user
			const tokens = await locals.directusInstance.login(form.data.email || '', form.data.password);

			// Get the circle ID's of the user
			const fetchedCircles = await locals.directusInstance.request(
				readItems("circles", {
					fields: ["circle_name", "circle_id"]
					// TODO: user_circle should also contain the role of the user in the circle -> Wagner
					// TODO: store the role for each circle in the cookie?
				})
			);

			// Create an array of objects with the circle name and id
			const circles = [...fetchedCircles.map(circle => ({
				name: circle.circle_name,
				id: circle.circle_id,
			}))];

			// Make sure the cookie is only sent for /app routes, not when resources (img etc.) are fetched directly from directus
			cookies.set('circles', JSON.stringify(circles).replace(/\//g, ''), { path: '/' });

			cookies.set('access_token', tokens.access_token || "", { path: '/' });
			cookies.set('refresh_token', tokens.refresh_token || "", { path: '/' });

			console.debug("[LOGIN]", circles);

		} catch (e) {
			console.error("[LOGIN]", e);
			return setError(form, '', 'Die Email oder das Passwort ist falsch.');
		}

		redirect(307, route('/'), { type: 'success', message: "Moin!" }, cookies);

	}
} satisfies Actions;

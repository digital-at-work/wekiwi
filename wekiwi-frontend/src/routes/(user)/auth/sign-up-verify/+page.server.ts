import type { PageServerLoad } from './$types';

import { setFlash, redirect } from 'sveltekit-flash-message/server';

import { updateUser, createFolder } from '@directus/sdk';

import { route } from '$lib/ROUTES';

import { env } from '$env/dynamic/private';

const DIRECTUS_ADMIN_KEY = env.DIRECTUS_ADMIN_KEY;


export const load: PageServerLoad = async (event) => {
	const { locals, cookies, url } = event;

	if (locals.user) {
		console.log("[SIGN-UP] User is already logged in, redirecting to /")		
		redirect(307, route('/'));
	}
	try {
		const username = url.searchParams.get('usrn');
		const user_id = url.searchParams.get('usri');

		if (!username || !user_id) {
			redirect(302, route('/auth/sign-in'), { type: 'error', message: "Du kannst dich nur mit einem Registierungslink verifizieren. Bitte versuche es erneut oder kontaktiere uns." }, cookies);
		}

		locals.directusInstance.setToken(DIRECTUS_ADMIN_KEY)
		const user_folder = await locals.directusInstance.request(createFolder({ name: username, parent: 'ec201009-b69a-4bee-8b3d-ae24fe220cc7' }))

		console.log('user_folder', user_folder)
		// @ts-ignore
		await locals.directusInstance.request(updateUser(user_id, { status: "active", user_folder: { id: user_folder.id }, role: { id: 'e692c7c2-6c8b-40e5-90e5-d15b972d3583' } }))


	} catch (err: any) {
		console.error(`Registration error: ${JSON.stringify(err)}`)
		redirect(302, route('/auth/sign-up'), { type: 'error', message: "Leider ist bei der verifizierung ein Fehler aufgetreten. Bitte versuche es erneut oder kontaktiere uns." }, cookies);
	}

	redirect(301, route('/auth/sign-in'), { type: 'success', message: "Du bist jetzt verifiziert und kannst dich einloggen! Los gehts :-)" }, cookies);
}
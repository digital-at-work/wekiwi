import type { PageServerLoad, Actions } from './$types';

import { fail, redirect } from '@sveltejs/kit';

import { setError, superValidate } from 'sveltekit-superforms';
import { resetPasswordSchema } from '$lib/config/zod-schemas';
import { zod } from 'sveltekit-superforms/adapters';

import { route } from '$lib/ROUTES';

import { passwordRequest } from '@directus/sdk';

import { env } from '$env/dynamic/public';
import { setFlash } from 'sveltekit-flash-message/server';



export const load: PageServerLoad = async (event) => {
	const form = await superValidate(event, zod(resetPasswordSchema));
	return {
		form
	};
};

/** @satisfies {import('./$types').Actions} */
export const actions = {
	default: async (event) => {
		const form = await superValidate(event, zod(resetPasswordSchema));

		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		try {
			await event.locals.directusInstance.request(passwordRequest(form.data.email || "", `${env.PUBLIC_FRONTEND_URL}${route('/auth/password/update')}`));
		} catch (e) {
			console.error(e);
			return setError(
				form,
				'',
				'Es gab ein Problem beim Zurücksetzen Deines Passworts. Bitte kontaktiere uns, wenn du Hilfe benötigst'
			);
		}
		setFlash({ type: 'success', timeout: 4000, message: "Wir haben Dir eine E-Mail mit einem Link zum Zurücksetzen Deines Passworts gesendet. Bitte überprüfe Dein Postfach." }, event.cookies);
	}
} satisfies Actions;

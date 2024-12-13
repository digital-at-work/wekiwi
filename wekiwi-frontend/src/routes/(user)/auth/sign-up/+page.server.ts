import { fail } from '@sveltejs/kit';

import { route } from '$lib/ROUTES';

import type { PageServerLoad, Actions } from './$types';

import { superValidate, setError } from 'sveltekit-superforms';
import { signUpSchema } from '$lib/config/zod-schemas';
import { zod } from 'sveltekit-superforms/adapters';
import { redirect } from 'sveltekit-flash-message/server';

import { triggerFlow, createUser } from '@directus/sdk';

import { setFlash } from 'sveltekit-flash-message/server';

import CryptoJS from 'crypto-js'

import { env } from '$env/dynamic/private';



const INVITE_SECRET = env.INVITE_SECRET;
const DIRECTUS_ADMIN_KEY = env.DIRECTUS_ADMIN_KEY;

export const load: PageServerLoad = async (event) => {
	if (event.locals.user) {
		console.log("[SIGN-UP-VERIFY] User is already logged in, redirecting to /")		
		redirect(307, route('/'));
	}

	return {
		form: await superValidate(event, zod(signUpSchema))
	};
};

/** @satisfies {import('./$types').Actions} */
export const actions = {
	signUp: async (event) => {
		const { locals, url, cookies } = event;
		const form = await superValidate(event, zod(signUpSchema));

		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		try {
			const encryptedCircles = url.searchParams.get('circles');

			let decryptedCircles: { circle_id: number, role: string }[] = [];
			try {
				if (encryptedCircles) {
					const bytes = CryptoJS.AES.decrypt(encryptedCircles, INVITE_SECRET);
					decryptedCircles = JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
				}

			} catch (e) {
				setFlash({ type: 'error', message: "Da stimmt etwas nicht... Bitte versuche es erneut oder kontaktiere uns." }, cookies);
				return
			}

			locals.directusInstance.setToken(DIRECTUS_ADMIN_KEY)
			const user_info = await locals.directusInstance.request(createUser({ ...form.data, password: `${form.data.password}`, date_joined: new Date().toISOString(), status: 'Draft', user_circles: [...decryptedCircles] }, { fields: ['id', 'email', 'username'] }))

			await locals.directusInstance.request((triggerFlow('POST', '11212220-0c95-4201-b6d7-8bf26e09bf0f', { 'username': form.data.username, 'user_id': user_info.id, 'email': user_info.email! })))

		} catch (err: any) {
			console.error(`registration error ${JSON.stringify(err)}`)
			return setError(form, '', `Bitte versuche es erneut. Leider ist folgender Fehler aufgetreten.`);
		}
		redirect(301, route('/auth/sign-in'), { type: 'success', timeout: 4000, message: "Bitte bestätige Deine Registierung mit dem Link in der Email, die wir dir geschickt haben." }, cookies);

	}
} satisfies Actions;
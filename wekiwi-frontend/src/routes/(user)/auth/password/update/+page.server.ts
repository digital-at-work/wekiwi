import type { PageServerLoad, Actions } from './$types';

import { fail } from '@sveltejs/kit';

import { route } from '$lib/ROUTES';

import { setError, superValidate } from 'sveltekit-superforms';
import { userUpdatePasswordSchema } from '$lib/config/zod-schemas';
import { zod } from 'sveltekit-superforms/adapters';
import { redirect } from 'sveltekit-flash-message/server';

import { passwordReset } from '@directus/sdk';


export const load: PageServerLoad = async (event) => {
    const form = await superValidate(event, zod(userUpdatePasswordSchema));
    return {
        form
    };
};

export const actions = {
    default: async (event) => {
        const { url, locals, cookies } = event;
        const form = await superValidate(event, zod(userUpdatePasswordSchema));

        if (!form.valid) {
            return fail(400, {
                form
            });
        }

        const reset_token = url.searchParams.get('token');
        if (!reset_token) {
            return setError(form, '', 'Ungültiger Reset-Token. Bitte fordere einen neuen Link an.');
        }

        try {
            await locals.directusInstance.request(passwordReset(reset_token, form.data.password));
        } catch (e) {
            console.error(e);
            return setError(
                form,
                '',
                'Es gab ein Problem beim Ändern Deines Passworts. Bitte kontaktiere uns, wenn du Hilfe benötigst'
            );
        }

        redirect(302, route('/auth/sign-in'), { type: 'success', message: "Dein Passwort wurde erfolgreich geändert. Du kannst dich jetzt einloggen." }, cookies);

    }
} satisfies Actions;
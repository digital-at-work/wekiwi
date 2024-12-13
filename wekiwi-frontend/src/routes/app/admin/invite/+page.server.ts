import type { PageServerLoad, Actions } from './$types';

import { fail } from '@sveltejs/kit';

import { superValidate } from 'sveltekit-superforms';
import { inviteSchema } from '$lib/config/zod-schemas';
import { zod } from 'sveltekit-superforms/adapters';

import CryptoJS from 'crypto-js'

import { env } from '$env/dynamic/private';
const INVITE_SECRET = env.INVITE_SECRET;

import { route } from '$lib/ROUTES';

import { inviteUser } from '@directus/sdk';

import { setFlash } from 'sveltekit-flash-message/server';


export const load: PageServerLoad = async (event) => {
    return {
        form: await superValidate(event, zod(inviteSchema))
    };
};

export const actions = {
    async default(event) {
        
        const form = await superValidate(event, zod(inviteSchema));

        if (!form.valid) {
            return fail(400, {
                form
            });
        }

        try {
            const encryptedCircles = CryptoJS.AES.encrypt(JSON.stringify(form.data.circles), INVITE_SECRET).toString();
            const invitationURL = route("/auth/sign-up", { inv: encodeURIComponent(encryptedCircles) });

            event.locals.directusInstance.request(inviteUser(form.data.recipientEmail, 'circleUser', invitationURL));

        } catch (e) {
            setFlash({type: 'error', message: 'Einladung konnte nicht versendet werden.'}, event.cookies);
        }
    }
} satisfies Actions;

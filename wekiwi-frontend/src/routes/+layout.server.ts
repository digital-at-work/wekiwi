import type { LayoutServerLoad } from './$types';
import { loadFlash } from 'sveltekit-flash-message/server';

import { contentShareSchema } from '$lib/config/zod-schemas';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';

import { readMe } from '@directus/sdk';


export const load = loadFlash(async ({locals}) => {
    let user = undefined;

    // load user info
    if (locals.user) {
        const userInfo = await locals.directusInstance.request(readMe({
            fields: ['username', 'avatar', 'first_name', 'last_name', 'company_id', 'email'],
        }));
        console.debug('[ROOT LAYOUT] User:', JSON.stringify(userInfo));
        const { token, ...userLocals } = locals.user;
        user = { ...userLocals, ...userInfo };
        
    }

    const contentShareForm = await superValidate(zod(contentShareSchema));

    return {
        user: user,
        contentShareForm
    };
}) satisfies LayoutServerLoad;

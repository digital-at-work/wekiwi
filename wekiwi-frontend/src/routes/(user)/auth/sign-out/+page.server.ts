import type { Actions } from './$types';

import { redirect } from 'sveltekit-flash-message/server';

import { route } from '$lib/ROUTES';


export const actions = {
	default: async ({cookies}) => {
		
		cookies.delete('circles', { path: '/' });
		cookies.delete('access_token', { path: '/' });
		cookies.delete('refresh_token', { path: '/' });

		redirect(route('/'), { type: 'info', message: "Bis bald! :-)" }, cookies);

	}
} satisfies Actions;

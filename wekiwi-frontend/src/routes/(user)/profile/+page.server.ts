import type { PageServerLoad } from './$types';

import { fail, error } from '@sveltejs/kit';

import { superValidate } from 'sveltekit-superforms';
import { profileSchema } from '$lib/config/zod-schemas';
import { zod } from 'sveltekit-superforms/adapters';

import { readMe, readAssetRaw, updateMe, uploadFiles } from '@directus/sdk';

import { setFlash } from 'sveltekit-flash-message/server';


export const load: PageServerLoad = async ({ locals, parent }) => {

	const { user } = await parent();

	const profileData = await locals.directusInstance.request(readMe({
		fields: ['first_name', 'last_name', 'email', 'bio', 'interests', 'avatar'],
	}));

	let profilePicture: File | undefined;

	if (profileData.avatar) {
		const stream = await locals.directusInstance.request(readAssetRaw(profileData?.avatar as string));

		const reader = stream.getReader();
		const chunks = [];
		while (true) {
			const { done, value } = await reader.read();
			if (done) break;
			chunks.push(value);
		}

		profilePicture = new File(chunks, profileData?.avatar as string, { type: 'image/jpeg' });
	}

	const form = await superValidate({
		...profileData,
		...user,
		avatar: profilePicture,
	},
		zod(profileSchema));

	return {
		form
	};
}


export const actions = {
	save: async (event) => {
		const { cookies, locals } = event;
		if (!locals.user) throw error(401);

		const form = await superValidate(event, zod(profileSchema));

		if (!form.valid) {
			return fail(400, {
				form
			});
		}

		try {
			const formData = new FormData();

			if (form.data.avatar) {
				formData.append('file', form.data.avatar);
			}

			const uploadedFile = await locals.directusInstance.request(uploadFiles(formData));

			const updatedFormData = {
				...form.data,
				avatar: uploadedFile.id
			};

			await locals.directusInstance.request(updateMe(updatedFormData));

			setFlash({ type: 'success', message: 'Änderungen gespeichert.' }, cookies);
		}
		catch (e: any) {
			console.error(e);
			setFlash({ type: 'error', message: 'Fehler beim Speichern der Änderungen.' }, cookies);
		}

		return { form };
	}
};
import type { LayoutServerLoad } from './$types';

import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { contentCreateSchema } from '$lib/config/zod-schemas';


export const load: LayoutServerLoad = async () => {

    const contentCreateForm = await superValidate(zod(contentCreateSchema));

	return {
        contentCreateForm
	};
}
import type { LayoutServerLoad } from './$types';

import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { contentCreateSchema, contentEditSchema } from '$lib/config/zod-schemas';


export const load: LayoutServerLoad = async () => {

    const contentCreateForm = await superValidate(zod(contentCreateSchema));
    const contentEditForm = await superValidate(zod(contentEditSchema));
    const subContentEditForm = await superValidate(zod(contentEditSchema));

	return {
        contentCreateForm,
        contentEditForm,
        subContentEditForm
	};

}
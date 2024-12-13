import type { PageServerLoad } from './$types';

import { readItems } from '@directus/sdk';

export const load = (async ({locals}) => {

    if (locals.user?.circles && !!locals.user?.circles?.length) {
        const circles = await locals.directusInstance.request(readItems('circles', {
            filter: {
                circle_id: {
                    _in: locals.user.circles.map((obj: { id: string }) => Number(obj.id))
                }
            },
            fields: ['circle_id', 'circle_name', 'circle_avatar', 'description']
        }));
        return {
            circles
        };
    }


}) satisfies PageServerLoad;
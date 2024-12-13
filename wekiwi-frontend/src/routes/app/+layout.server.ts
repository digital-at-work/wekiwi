import type { LayoutServerLoad } from './$types';
import { readUsers } from '@directus/sdk';


export const load = (async ({ locals, url }) => {
    const circles = JSON.parse(url.searchParams.get('circles') || '[]');

    return {
        // Streamed promise
        circleUsers: locals.directusInstance.request(readUsers(
            {
                filter: {
                    "_and": [
                        ...((circles && circles.length > 0) ? [{
                            user_circles:
                            {
                                circle_id: { _in: circles }
                            }
                        }] : []),
                        { 'id': { _neq: locals.user.id } }
                    ]
                },
                fields: ['username', 'first_name', 'last_name']
            }
        )),
    };
}) satisfies LayoutServerLoad;
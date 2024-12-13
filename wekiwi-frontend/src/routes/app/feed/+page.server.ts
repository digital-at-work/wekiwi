import type { PageServerLoad } from './$types';

import { error } from '@sveltejs/kit';

import { route } from '$lib/ROUTES';

import { readItems } from '@directus/sdk';
import { requestContents, requestVectorContents } from '$lib/directus/requests.js'

import { setFlash, redirect } from 'sveltekit-flash-message/server';

import { env } from '$env/dynamic/private';


export const load: PageServerLoad = (async ({ locals, url, params, setHeaders, cookies, fetch, depends, untrack }) => {
    depends('data:feed');

    // Tells the browser to cache the page for 3s
    setHeaders({
        'Cache-Control': 'private, max-age=3'
    });

    // TODO: Page size should be a query parameter, because it can be different on mobile and should adjust to screen size
    const searchEncoded = url.searchParams.get('search') || '';

    // empty array will be ignored on filter
    const circles = JSON.parse(url.searchParams.get('circles') || '[]');

    let ai = untrack(() => url.searchParams.get('ai') === "true");
    let offset = untrack(() => Number(url.searchParams.get('offset') || 0))

    const type = url.searchParams.get('type') || 'text';
    const search = decodeURIComponent(searchEncoded) || '';

    const sort1 = url.searchParams.get('sort1') || '-date_created';
    const sort2 = url.searchParams.get('sort2') || '';

    const usercreated = url.searchParams.get('usercreated') || null;
    const userupdated = url.searchParams.get('userupdated') || null;

    const datecreated1 = url.searchParams.get('datecreated1') || '';
    const datelogic1 = url.searchParams.get('datelogic1') || '';
    const datecreated2 = url.searchParams.get('datecreated2') || '';

    const dateupdated1 = url.searchParams.get('dateupdated1') || '';
    const datelogic2 = url.searchParams.get('datelogic2') || '';
    const dateupdated2 = url.searchParams.get('dateupdated2') || '';

    if (!['document', 'text', 'image', 'audio'].includes(type)) {
        error(400, 'Inhaltstyp ungültig.')
    }

    const company_id = url.searchParams.get('c_id') || '';

    if (!company_id) {
        error(400, 'Ein interner Fehler ist passiert: fehlende Unternehmens-ID. Du kannst leider nichts tun, außer dem we:kiwi Team darüber zu berichten.');
    }

    //const startTime = performance.now();
    console.log(`[FEED] Started with the params:`, JSON.stringify(params));

    try {
        const response = (!ai || search.trim().length === 0) ? await locals.directusInstance.request(
            readItems('contents',
                // @ts-ignore
                requestContents(
                    type,
                    circles,
                    search,
                    company_id,
                    sort1,
                    sort2,
                    usercreated,
                    userupdated,
                    datecreated1,
                    datelogic1,
                    datecreated2,
                    dateupdated1,
                    datelogic2,
                    dateupdated2,
                    offset,
                )
            )
        ) : await fetch(route('ai', { ai_slug: '/v1/content/search' }), {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${env.AI_API_KEY}`,
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                requestVectorContents(
                    type,
                    circles,
                    search,
                    company_id,
                    usercreated,
                    userupdated,
                    datecreated1,
                    datelogic1,
                    datecreated2,
                    dateupdated1,
                    datelogic2,
                    dateupdated2,
                    offset
                ))
        }).then(res => res.json());

        console.log(`[FEED] Response:`, response);


        return {
            contents: response,
        }

    } catch (err: any) {
        console.error(`[FEED] Error (ai: ${ai}):`, err);
        if (ai) {
            redirect(301, route('/app/feed', { ...Object.fromEntries(url.searchParams), ai: "false" }), { type: 'error', message: `Es tut uns leid, die we:kiwi KI ist gerade nicht erreichbar. Bitte versuche die Suche ohne KI.` }, cookies);
        } else {
            setFlash({ type: 'error', message: `Fehler beim Laden des Feeds bzw. der Suche.` }, cookies);
        }
    }
}) satisfies PageServerLoad;
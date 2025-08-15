import type { Actions } from './$types';

import { route } from '$lib/ROUTES'

import { superValidate, withFiles, fail } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { contentCreateSchema } from '$lib/config/zod-schemas';
import { createItem, uploadFiles, triggerFlow, readMe } from '@directus/sdk';

import { setFlash } from 'sveltekit-flash-message/server';

export const actions = {
	createContent: async ({ locals, url, request, cookies }) => {
		console.log('[CONTENT_CREATE] Action started.'); // Added log
		const form = await superValidate(request, zod(contentCreateSchema));

		if (!form.valid) {
			console.log('[CONTENT_CREATE] Form validation failed:', form.errors); // Added log
			return fail(400, withFiles({ form }));
		}

		console.log('[CONTENT_CREATE] Form validated successfully.'); // Added log

        const mentions = Array.isArray(form.data.mentions)
        ? form.data.mentions
        : (typeof form.data.mentions === 'string' ? JSON.parse(form.data.mentions) : []);

		console.log("Mentions received in backend action:", form.data.mentions);

        const type = url.searchParams.get('type') || '';
        if (!type) {
            setFlash({ type: 'error', message: 'Inhaltstyp fehlt.' }, cookies);
            return fail(400, withFiles({ form }));
        }

        const company_id = url.searchParams.get('c_id');
        if (!company_id) {
            setFlash({ type: 'error', message: 'Unternehmen fehlt.' }, cookies);
            return fail(400, withFiles({ form }));
        }

        const circles = form.data.circles.map((value: number) => ({ circle_id: value }));
        const parent_id = Number(url.searchParams.get('parent_id')) || null;

        try {
            let files: { id: string, content_type: string, type: string | null }[] = [];

            if (form.data.files && form.data.files.length > 0 && form.data.files[0]) { // Check if files exist and array is not empty
				console.log(`[CONTENT_CREATE] Attempting to upload ${form.data.files.length} file(s).`); // Added log
				form.data.files.forEach((file: File | undefined, index: number) => {
					if (file) {
						console.log(`[CONTENT_CREATE] File ${index + 1}: Name=${file.name}, Size=${file.size}, Type=${file.type}`); // Added log
					}
				});

                const userInfo = await locals.directusInstance.request(readMe({
                    fields: [{ user_folder: ['id'] }],
                }))

                const formData = new FormData();
                form.data.files.forEach((file: File | undefined) => {
                    if (file) {
                        formData.append('folder', userInfo.user_folder?.id ?? 'ec201009-b69a-4bee-8b3d-ae24fe220cc7')
                        formData.append('file', file);
                    }
                });

				console.log('[CONTENT_CREATE] FormData prepared. Calling uploadFiles...'); // Added log
                const uploadedFiles = await locals.directusInstance.request(uploadFiles(formData));
				console.log('[CONTENT_CREATE] uploadFiles call successful.'); // Added log
                files.push(...(Array.isArray(uploadedFiles) ? uploadedFiles : [uploadedFiles]));
            } else {
				console.log('[CONTENT_CREATE] No files attached to upload.'); // Added log
			}

            const content = await locals.directusInstance.request(createItem('contents', {
                title: form.data.title,
                text: form.data.text,
                content_type: type,
                circle_contents: circles,
                parent_id: parent_id,
                company_id: Number(company_id),
                to_be_parsed_by_directus_flow: form.data.to_be_parsed_by_directus_flow,
                child_id: files.length > 0 ? files.map((file) => {
                    if (!file.type) return null;

                    let content_type;

                    if (file.type.startsWith('image/')) {
                        content_type = 'image';
                    } else if (file.type.startsWith('audio/')) {
                        content_type = 'audio';
                    } else {
                        content_type = 'document';
                    }

                    return {
                        company_id: Number(company_id),
                        file_id: file.id,
                        content_type: content_type,
                        to_be_parsed_by_directus_flow: content_type === 'document' ? form.data.to_be_parsed_by_directus_flow : false,
                        circle_contents: circles
                    };
                }) : null
            }, {
                fields: [
                    "content_id",
                    'date_created',
                    'content_type',
                    'parent_id',
                    {
                        circle_contents: ['circle_id']
                    },
                    {
                        user_created: ['avatar', 'username'],
                        user_updated: ['avatar', 'username'],
                    },
                    {
                        child_id: [
                            {
                                file_id: ['filename_disk', 'id']
                            }
                        ]
                    }
                ]
            }));

            if (mentions.length > 0) {
                await locals.directusInstance.request(triggerFlow('POST', '45ae3423-dd27-4d87-a954-49d7964c6e92', {
                    usernames: JSON.stringify(mentions.map((user: { username: string }) => user.username)),
                    from_username: locals.user.id,
                    content_id: content.content_id.toString(),
                }));
            }

            if (!parent_id) setFlash({ type: 'success', message: `Der Inhalt wurde erstellt. Es dauert kurz bis die KI-Suche ihn finden kann. <a class="anchor" href="${route('/app/[content_id=integer]', { content_id: content.content_id.toString(), circles: JSON.stringify(form.data.circles) })}">Zum Beitrag</a>`, timeout: 3500 }, cookies);
            return withFiles({ form, content: content });
        } catch (err: any) {
            console.error(`[CONTENT_CREATE] Error during content creation or file upload.`); // Modified log
			console.error('[CONTENT_CREATE] Upload Error Details:', err); // Added detailed error log
            setFlash({ type: 'error', message: `Fehler bei der Erstellung des Inhalts` }, cookies);
            // Return 400 if it's likely a client/proxy issue, otherwise 500
            const statusCode = err.status === 400 || err.message?.includes('400') || err.message?.includes('Bad Request') ? 400 : 500;
            return fail(statusCode, withFiles({ form }));
        }
    }
    // uploadDocument: async ({ locals, request, cookies }) => {
    //     const form = await superValidate(request, zod(filesUploadSchema));

    //     if (!form.valid) {
    //         return fail(400, withFiles({ form }));
    //     };

    //     const formData = new FormData();
    //     form.data.files.forEach((file: Blob | undefined) => {
    //         if (file) formData.append('file', file);
    //     });

    //     try {
    //         const response = await locals.directusInstance.request(uploadFiles(formData));
    //         setFlash({ type: 'success', message: 'Dateien erfolgreich hochgeladen.' }, cookies);
    //     } catch (err: any) {
    //         setFlash({ type: 'error', message: `Fehler beim Hochladen der Dateien: ${err.message}` }, cookies);
    //     }
    // }
} satisfies Actions;

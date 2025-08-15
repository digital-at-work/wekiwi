import type { PageServerLoad, Actions } from './$types';

import { error } from '@sveltejs/kit';

import { superValidate, withFiles, fail } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { contentShareSchema, contentEditSchema } from '$lib/config/zod-schemas';

import { readItem, deleteItem, deleteItems, updateItem, createShare, readUsers, createItem, createItems, triggerFlow, readItems, authenticateShare, readMe, uploadFiles } from '@directus/sdk';

import { setFlash } from 'sveltekit-flash-message/server';

import { ReactionType } from '$lib/config/constants'
import { number } from 'zod';


export const load: PageServerLoad = async ({ locals, url, params, setHeaders }) => {
	if (!params.content_id) return fail(400, { message: 'Inhalts ID fehlt.' });

	// Tells the browser to cache the page for 2s
	setHeaders({
		'Cache-Control': 'private, max-age=2'
	});

	const share_key = url.searchParams.get('share_key') || '';
	const password = url.searchParams.get('password') || '';

	if (share_key) {
		const tokens = await locals.directusInstance.request(authenticateShare(share_key, password));
		locals.directusInstance.setToken(tokens.access_token);
	}

	const response = await locals.directusInstance.request(readItem('contents', params.content_id, {
		deep: {
			// @ts-ignore
			interaction_id: {
				_filter: {
					interaction_type: {
						_eq: 'like'
					},
				},
			},
			child_id: {
				// @ts-ignore
				interaction_id: {
					_filter: {
						interaction_type: {
							_eq: 'like',
						},
					},
				},
			}
		},
		fields: [
			"content_id",
			'content_type',
			"title",
			"text",
			'date_created',
			'date_updated',
			'parent_id',
			{
				interaction_id: ['interaction_id']
			},
			{
				circle_contents: ['circle_id']
			},
			{
				user_created: ['avatar', 'username'],
				user_updated: ['avatar', 'username'],
			},
			{
				child_id: [
					'content_id',
					'title',
					'text',
					'date_created',
					'content_type',
					'parent_id',
					{
						interaction_id: ['interaction_id']
					},
					{
						child_id: [
							'content_id',
							{
								file_id: ['filename_disk', 'id']
							}
						]
					},
					{
						file_id: ['filename_disk', 'id']
					},
					{
						user_created: ['avatar', 'username'],
						user_updated: ['avatar', 'username']
					},
				],
			},
		]
	}))
	return {
		content: response
	};
}


export const actions = {
	updateContent: async ({ locals, params, request, cookies, url }) => {
		const form = await superValidate(request, zod(contentEditSchema));
		if (!form.valid) {
			return fail(400, withFiles({ form }));
		}

		if (!params.content_id) {
			setFlash({ type: 'error', message: 'Inhalts ID fehlt.' }, cookies);
			return fail(400, withFiles({ form }));
		}

		const circles = form.data.circles.map((value: number) => ({ circle_id: value }))

		const company_id = url.searchParams.get('c_id');
		if (!company_id) {
			setFlash({ type: 'error', message: 'Unternehmen fehlt.' }, cookies);
			return fail(400, withFiles({ form }));
		}
		
		try {
			let files: { id: string, content_type: string, type: string | null }[] = [];
			let newAttachments: any = [];

			if (form.data.files[0]) {

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

				const uploadedFiles = await locals.directusInstance.request(uploadFiles(formData));
				files.push(...(Array.isArray(uploadedFiles) ? uploadedFiles : [uploadedFiles]));

				// This should work (creating all content / attachments at once), but doesn't... 
				// newAttachments = await locals.directusInstance.request(createItems('contents', files.map((file) => ({
				// 	company_id: Number(company_id),
				// 	file_id: file.id,
				// 	content_type: file.content_type,
				// 	circle_contents: circles
				// })) && [], {
				// 	fields: [
				// 		"content_id",
				// 	]
				// }))

				// So we have to create the individual items
				const newAttachmentReq = files.map((file) => {
					if (!file.type) return null;

					let content_type;

					if (file.type.startsWith('image/')) {
						content_type = 'image';
					} else if (file.type.startsWith('audio/')) {
						content_type = 'audio';
					} else {
						content_type = 'document';
					}

					return locals.directusInstance.request(
						createItem(
							'contents',
							{
								company_id: +company_id,
								file_id: file.id,
								content_type: content_type,
								circle_contents: circles,
							},
							{
								fields: [
									"content_id"
								]
							}
						)
					)
				});

				newAttachments = await Promise.all(newAttachmentReq);
			}

			const content = await locals.directusInstance.request(updateItem('contents', params.content_id, {
				...(form.data.title && { title: form.data.title }),
				...(form.data.text && { text: form.data.text }),
				//...(type && { content_type: type }), //not changeable
				//...(parent_id && { parent_id: Number(parent_id) }), //not changeable
				...(circles && { circle_contents: circles }),
				child_id: [
					// existing children
					...(form.data.child_ids || []).map((child) => {
						return {
							content_id: child.content_id,
							circle_contents: circles,
							// add attachments, if there are any 
							...(!!child?.attachment_ids?.length && {
								child_id: child.attachment_ids?.map((id) => {
									return { content_id: id, circle_contents: circles }
								})
							})
						}
					}),
					// new attachments
					...newAttachments.map((attachment: { content_id: number }) => {
						return { content_id: attachment.content_id }
					})
				],
			}, {
				deep: {
					// @ts-ignore
					child_id: {
						_filter: {
							file_id: {
								_nnull: true
							},
						},
					}
				},
				filter: {
					company_id: {
						_eq: +company_id
					}
				},
				fields: [
					"content_id",
					'date_created',
					'date_updated',
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
							"content_id",
							{
								file_id: ['filename_disk', 'id']
							}
						]
					}
				]
			}));
			if (form.data.mentions) {
				await locals.directusInstance.request(triggerFlow('POST', '45ae3423-dd27-4d87-a954-49d7964c6e92', {
					usernames: JSON.stringify(form.data.mentions),
					from_username: locals.user.id,
					content_id: params.content_id,
				}));
			}
			return withFiles({ form, content: content });
		} catch (err: any) {
			console.error(`[CONTENT] Error`, err);
			setFlash({ type: 'error', message: `Fehler bei der Aktualisierung: ${err.errors[0].message}` }, cookies);
		}
	},
	contentReaction: async ({ locals, params, url, cookies }) => {
		if (!params.content_id) {
			setFlash({ type: 'error', message: 'Content_id fehlt.' }, cookies);
			return;
		}

		const reaction = url.searchParams.get('reaction_type');
		if (!reaction || !Object.values(reaction).includes(reaction as ReactionType)) {
			setFlash({ type: 'error', message: 'Inhaltstyp fehlt.' }, cookies);
			return;
		}

		try {
			const existingReaction = await locals.directusInstance.request(readItems('interactions', {
				filter: {
					content_id: { _eq: Number(params.content_id) },
					user_id: { _eq: Number(locals.user.id) },
					interaction_type: { _eq: reaction }
				},
				fields: [
					'interaction_id',
					'interaction_type'
				],
				limit: 1,
			}));

			if (existingReaction.length > 0) {
				if (
					(existingReaction[0].interaction_type === ReactionType.Like && reaction === ReactionType.Like) ||
					(existingReaction[0].interaction_type === ReactionType.Dislike && reaction === ReactionType.Dislike)
				) {
					// Remove like/dislike reactions if they already exist
					await locals.directusInstance.request(deleteItem('interactions', existingReaction[0].interaction_id));
					setFlash({ type: 'success', message: 'Reaction removed.' }, cookies);
				} else {
					// Update existing reaction to like/dislike
					await locals.directusInstance.request(updateItem('interactions', existingReaction[0].interaction_id, {
						interaction_type: reaction,
					}));
				}
			} else {
				// Create a new reaction
				await locals.directusInstance.request(createItem('interactions', {
					content_id: Number(params.content_id),
					user_id: locals.user.id,
					interaction_type: reaction,
				}));
			}
		} catch (err: any) {
			setFlash({ type: 'error', message: `Leider gab es einen Fehler... ${err.errors[0].message}` }, cookies);
		}
	},
	shareContent: async ({ locals, request, params, cookies }) => {
		const form = await superValidate(request, zod(contentShareSchema));
		if (!form.valid) {
			return fail(400, { form });
		}

		const content_id = params.content_id;

		try {

			const share = await locals.directusInstance.request(createShare({
				collection: 'contents',
				item: content_id,
				...form.data,
				date_end: form.data.date_end as "datetime"
			}));

			// Gather emails for usernames
			const usernames = form.data.usernames;
			let userEmails: string[] = [];

			if (usernames && usernames.length > 0) {
				const users = await locals.directusInstance.request(readUsers({
					filter: { username: { _in: usernames } },
					fields: ['email'],
				}));
				userEmails = users.map(user => user.email || "");
			}

			const initial_emails = form.data.emails;
			const combined_emails = [...initial_emails ?? [], ...userEmails] as string[];

			// Send email invitations
			if (combined_emails.length > 0) {
				// trigger a flow with an array of objects with properties share_key and emails
				await locals.directusInstance.request(triggerFlow('POST', '8fa95f26-fcec-4bc5-bb1b-d0507ba3b07d', {
					share_key: share.id,
					emails: JSON.stringify(combined_emails),
					content_id: content_id
				}));
			}

			setFlash({ type: 'success', message: 'Der Inhalt wurde erfolgreich geteilt.' }, cookies);
		} catch (err: any) {
			setFlash({ type: 'error', message: `Fehler: ${err.errors[0].message}` }, cookies);
		}
	},
	deleteContent: async ({ locals, params, cookies }) => {
		if (!params.content_id) {
			return fail(400, { message: 'Missing content ID.' });
		}

		const contentId = Number(params.content_id);

		/**
		 * Recursively deletes a content item and all its children (and grandchildren, etc.).
		 * Ensures that no foreign key constraint errors occur due to existing child references.
		 */
		const deleteContentRecursively = async (parentId: number) => {
			// Step 1: Fetch all children of the current content item
			const children = await locals.directusInstance.request(
				readItems('contents', {
					filter: { parent_id: { _eq: parentId } },
					fields: ['content_id']
				})
			);

			// Step 2: Recursively delete each child (in case it has its own children)
			for (const child of children) {
				await deleteContentRecursively(child.content_id);
			}

			// Step 3: After all children are deleted, delete the parent item itself
			await locals.directusInstance.request(deleteItems('contents', [parentId]));
		};

		try {
			await deleteContentRecursively(contentId);
		} catch (err: any) {
			console.error(
				'Failed to delete content recursively:',
				err?.errors?.[0]?.message || err.message
			);
			throw error(500, 'Failed to delete content item.');
		}
	}
} satisfies Actions;

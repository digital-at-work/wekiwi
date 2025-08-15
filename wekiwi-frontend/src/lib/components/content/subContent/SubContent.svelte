<script lang="ts">
	import { page } from '$app/stores';
	import { createEventDispatcher } from 'svelte';

	import { enhance as svelteenhance } from '$app/forms';

	import { route } from '$lib/ROUTES';

	import { Pencil, Check, X, Trash2, Download } from 'lucide-svelte';

	// Import marked for markdown parsing
	import { marked } from 'marked';

	import { ConicGradient } from '@skeletonlabs/skeleton';

	import { DEFAULT_PLACEHOLDER_AVATAR } from '$lib/config/constants';

	import { formatDate } from '$lib/utils';

	import type { PartialContent, PartialUser } from '$lib/directus/directus.types';

	import { contentEditSchema } from '$lib/config/zod-schemas';

	import { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import type { Infer } from 'sveltekit-superforms';

	import { getFlash } from 'sveltekit-flash-message';

	import Editor from '$lib/components/editor/Editor.svelte';
	import FileUpload from '$lib/components/ui/forms/FileUpload.svelte';

	//import { getStateContext } from '$lib/state';

	export let subContent: PartialContent;
	export let circleUsers: Promise<PartialUser[]>;
	export let parent_circles: number[] | undefined;
	export let isReadonly = !(subContent.user_created?.username === $page.data.user.username);
	export let subContentEditForm;

	const superform = superForm<Infer<typeof contentEditSchema>>(subContentEditForm, {
		id: `${subContent.content_id}`,
		dataType: 'json',
		validators: zodClient(contentEditSchema),
		resetForm: false,
		clearOnSubmit: 'none',
		invalidateAll: false,
		onSubmit: ({ cancel }) => {
			// TODO: check if anything actually was changed
			// cancel();
		},
		onResult({ result }) {
			if (result.type === 'success') {
				subContent = {
					...subContent,
					...result.data?.content,
					text: $form.text,
					title: $form.title
				};
				console.log('subContent: ', subContent);
			}
			isEditing = false;
		},
		onUpdated() {
			$form.circles = parent_circles as number[];
		}
	});

	const { form, errors, enhance, delayed, allErrors, validate } = superform;

	const dispatch = createEventDispatcher();
	//const { modifyContent } = getStateContext();

	let parent_id = subContent?.parent_id || '';

	$form.text = subContent?.text || '';
	$form.circles = parent_circles as number[];

	const flash = getFlash(page);

	let isEditing = false;
	let isDeleting = false;

	// Handle mentions data type conversion
	let mentions: { id: number; username: string; }[] = [];
	$: {
		if (typeof $form.mentions === "string") {
			try {
				const parsed = JSON.parse($form.mentions);
				if (Array.isArray(parsed)) {
					mentions = parsed
						.filter(item => item && typeof item === 'object' && 'id' in item && 'username' in item)
						.map(item => ({ id: Number(item.id), username: String(item.username) }));
				}
			} catch {
				mentions = [];
			}
		} else if (Array.isArray($form.mentions)) {
			mentions = $form.mentions
				.filter(item => item && typeof item === 'object' && 'id' in item && 'username' in item)
				.map(item => ({ id: Number(item.id), username: String(item.username) }));
		} else {
			mentions = [];
		}
	}
</script>

<div class="rounded-lg bg-white p-4">
	<form
		method="POST"
		enctype="multipart/form-data"
		action={route('updateContent /app/[content_id=integer]', {
			content_id: (subContent?.content_id || '').toString(),
			parent_id: (parent_id || '').toString(),
			c_id: $page.data.user?.company_id
		})}
		use:enhance
	>
		<div class="w-full">
			<div class="flex w-[70%] items-center {!isReadonly && 'ml-auto flex-row-reverse'}">
				<!-- Author Information -->
				<div class="flex flex-col items-center">
					<img
						src={subContent.user_created?.avatar
								? route('cms_proxy_images', {
										image_id: `${subContent.user_created?.avatar}`,
										display_config: 'user-preview'
									})
								: DEFAULT_PLACEHOLDER_AVATAR + subContent?.user_created?.username}
						class="h-10 w-10 rounded-full"
						alt={subContent?.user_created?.username ?? ''}
					/>
					<span class="text-sm font-medium mt-1">{subContent?.user_created?.username ?? ''}</span>
				</div>

				<!-- Display editor -->
				<div
					class="rounded-large card
					prose {!isReadonly && 'prose-primary bg-primary-500 text-white'}
					w-full border p-4"
				>
					{#if !isEditing}
						<!-- Display Content text with markdown parsing -->
						{@html subContent?.text ? marked(subContent.text) : ''}

						<!-- Display Attachments -->
						<div class="flex flex-col">
							{#each subContent.child_id || [] as attachment}
								{#if attachment?.file_id}
									<a
										href={route('cms_proxy_files', { file_id: attachment.file_id.id })}
										download={attachment.file_id.id}
										class="variant-soft btn chip hover:variant-filled"
									>
										<span>{attachment.file_id?.filename_disk}</span>
										<span><Download /></span>
									</a>
								{/if}
							{/each}
						</div>
					{:else}
						<!-- Display Editor and Fileupload -->
						<div class="mb-4 mt-2 text-justify">
							{#await circleUsers}
								Loading...
							{:then circleUsers}
								<Editor
									bind:htmlContent={$form.text}
									bind:readonly={isReadonly}
									bind:mentions={mentions}
									{circleUsers}
									on:blur={() => validate('text')}
								/>
								<input type="hidden" name="text" bind:value={$form.text} />
								<input type="hidden" name="mentions" bind:value={mentions} />
							{:catch error}
								<p class="text-error-500">{error.message}</p>
							{/await}
						</div>
						{#if $errors.text}<span class="text-error-500">{$errors.text}</span>{/if}
						{#if Array.isArray($errors.mentions) && $errors.mentions.length > 0}<span class="text-error-500">{$errors.mentions.join(", ")}</span>{/if}

						<!-- File Upload -->
						<FileUpload {superform} />

						<!-- Edit Attachments -->
						{#each $form.child_ids || [] as attachment}
							{@const filename_disk = subContent.child_id?.find(
								(child) => child.content_id === attachment.content_id
							)?.file_id?.filename_disk}
							{#if filename_disk}
								<button
									type="button"
									class="variant-soft chip hover:variant-filled"
									on:click={() => {
										// Remove the attachment's content_id from the form child_ids
										$form.child_ids = $form.child_ids?.filter(
											(child) => child.content_id !== attachment.content_id
										);
									}}
								>
									<span>{filename_disk}</span>
									<span><X color="red" /></span>
								</button>
							{/if}
						{/each}
						<input type="hidden" name="child_ids" bind:value={$form.child_ids} />
					{/if}
				</div>
			</div>

			<!-- Edit subContent -->
			<div class="mt-2 flex w-[70%] items-center justify-between {!isReadonly && 'ml-auto'}">
				<div class="ml-auto flex items-center gap-4">
					<!-- Date created -->
					<span class="text-sm font-light text-gray-600">
						{#if subContent?.date_created}
							{formatDate(subContent?.date_created)}
						{/if}
					</span>

					<div class="flex items-center gap-4">
						{#if !isReadonly}
							{#if !isEditing}
								<!-- Display edit button-->
								<button
									class="variant-filled-primary chip hover:variant-filled"
									aria-label="Edit subContent"
									on:click={() => {
										isEditing = !isEditing;
										// populate form child_ids with initial ids and their child_id (attachment) ids
										$form.child_ids = subContent?.child_id?.map((child) => ({
											content_id: child.content_id,
											// @ts-ignore
											attachment_ids: child.child_id?.flatMap((gc) => gc.file_id && [gc.content_id])
										}));
									}}
								>
									<Pencil />
								</button>
								<!-- Display delete button-->
								{#if isDeleting}
									<ConicGradient
										width="w-4"
										stops={[
											{ color: 'transparent', start: 0, end: 25 },
											{ color: 'rgb(var(--color-warning-800))', start: 75, end: 100 }
										]}
										spin={true}
									/>
								{:else}
									<button
										form={`delete_${subContent.content_id}`}
										class="variant-filled-error chip hover:variant-filled"
										aria-label="Delete comment"
										type="submit"
									>
										<Trash2 size={24} color="#ffffff" strokeWidth={1.5} />
									</button>
								{/if}
							{:else}
								<!-- Display submit and abort buttons -->
								<button
									type="submit"
									class="btn {$form.text && !$allErrors.length
										? 'variant-filled-primary'
										: 'variant-soft-secondary'}"
								>
									{#if $delayed}
										<ConicGradient
											width="w-4"
											stops={[
												{ color: 'transparent', start: 0, end: 25 },
												{ color: 'rgb(var(--color-primary-800))', start: 75, end: 100 }
											]}
											spin={true}
										/> Hochladen ...
									{:else}
										<Check size={24} strokeWidth={1.5} />
									{/if}
								</button>
								<button
									class="variant-filled-error chip hover:variant-filled"
									on:click={() => {
										isEditing = !isEditing;
										//restore form child_id with initial ids
										$form.child_ids = subContent?.child_id?.map((obj) => obj.content_id);
									}}
								>
									<X size={24} strokeWidth={1.5} />
								</button>
							{/if}
						{/if}
					</div>
				</div>
			</div>
		</div>
	</form>
	<!-- Action (delete) - forms can not be nested, see mdn -->
	<form
		id={`delete_${subContent?.content_id}`}
		method="POST"
		action={route('deleteContent /app/[content_id=integer]', {
			content_id: (subContent.content_id || '').toString()
		})}
		use:svelteenhance={() => {
			isDeleting = true;
			return async ({ update, result }) => {
				isDeleting = false;
				if (result.type === 'success') {
					dispatch('deleteContent', {
						content_id: subContent.content_id
					});
					//  Updating not required, because reloading post will load content anew
					// 	modifyContent(Number(subContent.content_id), null, null, 'delete');
					$flash = { type: 'success', message: 'Beitrag erfolgreich gelöscht.' };
					update({ invalidateAll: false });
				} else if (result.type === 'error') {
					$flash = { type: 'error', message: 'Fehler beim Löschen des Beitrags.' };
				}
			};
		}}
	/>
</div>

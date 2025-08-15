<script lang="ts">
	import { page } from '$app/stores';

	import { createEventDispatcher, onMount } from 'svelte';

	import { enhance as svelteenhance } from '$app/forms';

	import { route } from '$lib/ROUTES';

	import { Pencil, Check, X, Trash2, Download } from 'lucide-svelte';

	// Import marked for markdown parsing
	import { marked } from 'marked';

	import { ConicGradient, Avatar } from '@skeletonlabs/skeleton';

	import { DEFAULT_PLACEHOLDER_AVATAR } from '$lib/config/constants';

	import { formatDate } from '$lib/utils';

	import type { PartialContent, PartialUser } from '$lib/directus/directus.types';

	import { getFlash } from 'sveltekit-flash-message';

	import { contentEditSchema } from '$lib/config/zod-schemas';

	import FileUpload from '$lib/components/ui/forms/FileUpload.svelte';
	import CircleSelection from '$lib/components/ui/forms/CircleSelection.svelte';
	import Editor from '$lib/components/editor/Editor.svelte';

	import { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import type { Infer } from 'sveltekit-superforms';

	import { getStateContext } from '$lib/state';

	export let content: PartialContent;
	export let circleUsers: Promise<PartialUser[]>;
	export let content_circles: number[] | undefined;
	export let isReadonly = !(content.user_created?.username === $page.data.user.username);
	export let contentEditForm;

	const { modifyContent } = getStateContext();

	const dispatch = createEventDispatcher();
	const superform = superForm<Infer<typeof contentEditSchema>>(contentEditForm, {
		id: `${content.content_id}`,
		dataType: 'json',
		validators: zodClient(contentEditSchema),
		resetForm: false,
		clearOnSubmit: 'none',
		invalidateAll: false,
		onSubmit({ cancel }) {
			// TODO: check if anything was actually changed?
			// cancel();
		},
		onResult({ result }) {
			if (result.type === 'success') {
				// Combined Attachments and subContent, because (for parents) there is no difference between them by design
				const updatedAttachments = result.data?.content?.child_id || [];
				const subContent = content?.child_id?.filter((child) => !child.file_id) || [];

				const updatedContent = {
					...result.data?.content,
					text: $form.text,
					title: $form.title,
					child_id: [...subContent, ...updatedAttachments]
				};

				dispatch('contentChange', updatedContent);
				modifyContent(Number(content.content_id), updatedContent, null, 'update');
			}
			isEditing = false;
		},
		onUpdated() {
			$form.circles = content_circles as number[];
		}
	});

	const { form, errors, enhance, delayed, allErrors, validate } = superform;

	$form.circles = content_circles as number[];
	$form.text = content?.text || '';
	$form.title = content?.title || '';
	$form.child_ids = content?.child_id?.map((child) => ({
		content_id: child.content_id,
		attachment_ids: Array.isArray(child.child_id)
			? child.child_id.map((attachment: { content_id: number }) => attachment.content_id)
			: []
	}))

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

	const flash = getFlash(page);

	let isEditing = false;
	let isDeleting = false;

	onMount(() => {
		const params = new URLSearchParams(window.location.search);
		if (params.get('mode') === 'edit') {
			isEditing = true;
		}
	});

	function handleEditClick() {
		const params = new URLSearchParams(window.location.search);

		if (params.get('mode') === 'edit') {
			isEditing = !isEditing;
		} else {
			const url = `${route('/app/[content_id=integer]', {
				content_id: (content.content_id || '').toString()
			})}?c_id=${$page.data.user?.company_id}&mode=edit`;
			window.open(url, '_blank', 'noopener,noreferrer');
		}
	}
</script>

<div class="grid grid-rows-[auto_1fr_auto]">
	<!-- Action (update) -->
	<form
		method="POST"
		enctype="multipart/form-data"
		action={route('updateContent /app/[content_id=integer]', {
			content_id: (content.content_id || '').toString(),
			c_id: $page.data.user?.company_id
		})}
		use:enhance
	>
		<div class="page-section">
			<header>
				<!-- Content Title -->
				{#if !isEditing}
					<!-- Content Title -->
					<h1 class="h2 font-bold">
						{content?.title || ''}
					</h1>
				{:else}
					<!-- Edit Content title -->
					<input
						type="text"
						name="title"
						id="title"
						class="input h2 w-10/12 bg-white font-bold"
						placeholder="Inhalt: kurz gefasst"
						data-invalid={$errors.title}
						bind:value={$form.title}
					/>
				{/if}
			</header>
			<!-- Author Section -->
			<div class="flex items-center justify-between">
				<div class="flex items-center space-x-4">
					<div class="shrink-0">
						<!-- TODO: anchor tag once the profile page is set - href={route('/profile')} -->
						<Avatar
							width="w-8"
							src={content.user_created?.avatar
								? route('cms_proxy_images', {
										image_id: `${content.user_created?.avatar}`,
										display_config: 'user-preview'
									})
								: DEFAULT_PLACEHOLDER_AVATAR + content?.user_created?.username}
							alt={content?.user_created?.username}
						/>
					</div>

					<div>
						<div class="font-semibold">
							<!-- TODO: anchor tag once the profile page is set - href={route('/profile')} -->
							{content?.user_created?.username}
						</div>
						<span class="block text-sm text-gray-600">
							{#if content?.date_created}
								{formatDate(content.date_created)}
							{/if}
						</span>
					</div>
				</div>

				<!-- Edit Content -->
				<div class="flex items-center gap-4">
					{#if !isReadonly}
						{#if !isEditing}
							<!-- Display edit button-->
							<button
								class="variant-filled-primary chip hover:variant-filled"
								on:click={handleEditClick}
							>
								<span><Pencil strokeWidth={1.5} /></span>
							</button>
							<!-- Display delete button -->
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
									form={`delete_${content.content_id}`}
									class="variant-filled-error chip hover:variant-filled"
									type="submit"
								>
									<span><Trash2 strokeWidth={1.5} /></span>
								</button>
							{/if}
						{:else}
							<!-- Display submit and abort button -->
							<button
								type="submit"
								class="chip hover:variant-filled {$form.title && $form.text && !$allErrors.length
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
								on:click={() => (isEditing = !isEditing)}
							>
								<X size={24} strokeWidth={1.5} />
							</button>
						{/if}
					{/if}
				</div>
			</div>

			<hr class="my-4" />

			<!-- Main Content Body -->

			{#if !isEditing}
				<!-- Display Content: Display content text with markdown parsing -->
				<article class="prose">
					{@html content?.text ? marked(content.text) : ''}
				</article>
				<!-- Display Attachments -->
				<div class="flex flex-col">
					{#each content.child_id || [] as attachment}
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
				<!-- Edit Content: Display editor -->
				{#if !$page.data.user}
					<div>Please log in to edit content.</div>
				{:else}
					<div class="">
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
							<p class="text-error-500">Error: {error.message}</p>
						{/await}
					</div>

					{#if $errors.text}<span class="text-error-500">{$errors.text}</span>{/if}
					{#if Array.isArray($errors.mentions) && $errors.mentions.length > 0}<span class="text-error-500">{$errors.mentions.join(", ")}</span>{/if}

					<FileUpload {superform} />

					<!-- Edit Attachments -->
					{#each $form.child_ids || [] as attachment}
						{@const filename_disk = content.child_id?.find(
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
					<CircleSelection {superform} field="circles" />
				{/if}
			{/if}
		</div>
	</form>

	<!-- Action (delete) - forms can not be nested, see mdn -->
	<form
		id={`delete_${content?.content_id}`}
		method="POST"
		action={route('deleteContent /app/[content_id=integer]', {
			content_id: (content.content_id || '').toString()
		})}
		use:svelteenhance={() => {
			isDeleting = true;
			return async ({ update, result }) => {
				isDeleting = false;
				console.log(result);
				if (result.type === 'success') {
					modifyContent(Number(content.content_id), null, null, 'delete');
					$flash = { type: 'success', message: 'Beitrag erfolgreich gelöscht.' };
					update({ invalidateAll: false });
					history.back();
				} else {
					$flash = { type: 'error', message: 'Fehler beim Löschen des Beitrags.' };
				}
			};
		}}
	/>
</div>

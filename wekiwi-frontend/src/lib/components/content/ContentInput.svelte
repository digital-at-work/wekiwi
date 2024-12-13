<script lang="ts">
	import { page } from '$app/stores';

	import { invalidate } from '$app/navigation';

	import { superForm } from 'sveltekit-superforms';
	import { contentCreateSchema } from '$lib/config/zod-schemas';
	import type { Infer } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';

	import { SendHorizontal } from 'lucide-svelte';
	import { ConicGradient } from '@skeletonlabs/skeleton';

	import { DEFAULT_EDITOR_TXT } from '$lib/config/constants';
	import Editor from '$lib/components/editor/Editor.svelte';

	import { route } from '$lib/ROUTES';

	import { queryParameters, ssp } from 'sveltekit-search-params';

	import type { PartialUser } from '$lib/directus/directus.types';
	//import { getStateContext } from '$lib/state';

	import FileUpload from '$lib/components/ui/forms/FileUpload.svelte';
	import CircleSelection from '$lib/components/ui/forms/CircleSelection.svelte';
	import { createEventDispatcher } from 'svelte';

	export let readonly = false;
	export let circleUsers: Promise<PartialUser[]>;
	export let contentTitle = '';

	export let contentCreateForm;

	//const { modifyContent } = getStateContext();

	const superform = superForm<Infer<typeof contentCreateSchema>>(contentCreateForm, {
		onSubmit: async ({ formData }) => {
			formData.set('text', (formData.get('text') as string));
		},
		invalidateAll: false,
		validators: zodClient(contentCreateSchema),
		onResult({ result }) {
			if (result.type === 'success') {
				//modifyContent(result.data?.content, { ...result.data?.content, text: $form.text, title: $form.title }, null, 'add');
				//TODO: does this also work with content/create route (no modal)?
				invalidate('data:feed').then(() => {
					history.back();
				});
			}
		}
	});

	const { form, errors, enhance, delayed, allErrors, validate, validateForm } = superform;

	const searchparams = queryParameters({ circles: ssp.array() });
	if ($searchparams.circles) $form.circles = $searchparams.circles;

	$form.text = DEFAULT_EDITOR_TXT;
	$: $form.title = contentTitle;

	const dispatch = createEventDispatcher();
	function closeModal() {
		if (window.tinymce) {
			window.tinymce.remove();
			console.log('TinyMCE instances removed');	
		}
		dispatch('close');
	}

</script>

<div class="grid grid-rows-[auto_1fr_auto]">
	<!-- TODO: choose type for main content -->
	<form
		method="POST"
		enctype="multipart/form-data"
		action={route('createContent /app/content_create', {
			type: $searchparams.type || 'text',
			c_id: $page.data.user?.company_id
		})}
		use:enhance
	>
		<div class="page-section">
			<div class="flex flex-col">
				<span class="font-semibold">Titel</span>
				<input
					type="text"
					name="title"
					class="input h2 bg-white font-bold w-11/12"
					placeholder="Inhalt: kurz gefasst"
					data-invalid={$errors.title}
					bind:value={$form.title}
				/>
			</div>
			{#if $errors.title}<span class="text-error-500">{$errors.title}</span>{/if}
			<div class="flex flex-col">
				<span class="font-semibold">Inhalt</span>
				{#await circleUsers}
					Hochladen ...
				{:then circleUsers}
					<Editor
						bind:htmlContent={$form.text}
						bind:mentions={$form.mentions}
						bind:readonly
						{circleUsers}
						cssClasses="tinymce-wrapper p-2"
						height={450}
						on:blur={() => validate('text')}
					/>
					<input type="hidden" name="text" bind:value={$form.text} />
					<input type="hidden" name="mentions" bind:value={$form.mentions} />
				{:catch error}
					<p class="text-error-500">{error.message}</p>
				{/await}
			</div>
			{#if $errors.text}<span class="text-error-500">{$errors.text}</span>{/if}
			{#if $errors.mentions?._errors}<span class="text-error-500">{$errors.mentions?._errors}</span
				>{/if}
			<FileUpload {superform} />
			<CircleSelection {superform} field="circles" />
			<div class="flex justify-end">
				<button
					type="submit"
					class="btn {$form.title && $form.text && !$allErrors.length
						? 'variant-filled-primary'
						: 'variant-soft-secondary'}"
					on:click={closeModal}
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
						<span><SendHorizontal /></span>
						<span>Veröffentlichen</span>
					{/if}
				</button>
				<!-- Ask AI button (not necessary for now) -->
				<!-- <a href={route('/')} class="btn variant-soft-primary">Fragen</a> -->
			</div>
		</div>
	</form>
</div>

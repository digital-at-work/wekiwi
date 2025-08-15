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
	import FileUpload from '$lib/components/ui/forms/FileUpload.svelte';
	import CircleSelection from '$lib/components/ui/forms/CircleSelection.svelte';
	import { createEventDispatcher } from 'svelte';

	export let readonly = false;
	export let circleUsers: Promise<PartialUser[]>;
	export let contentTitle = '';
	export let contentCreateForm;

	const dispatch = createEventDispatcher();

	let mentions: { id: number; username: string }[] = [];

	const superform = superForm<Infer<typeof contentCreateSchema>>(contentCreateForm, {
		onSubmit: async ({ formData }): Promise<Infer<typeof contentCreateSchema>> => {
			$form.to_be_parsed_by_directus_flow = formData.get('to_be_parsed_by_directus_flow') === 'on';
			
			formData.set('text', formData.get('text') as string);
			formData.set('mentions', JSON.stringify(mentions));
			
			const payload = {
				text: formData.get('text') as string,
				mentions: JSON.parse(formData.get('mentions') as string),
				files: formData.getAll('files') as File[],
				circles: JSON.parse(formData.get('circles') as string),
				to_be_parsed_by_directus_flow: $form.to_be_parsed_by_directus_flow,
				title: formData.get('title') as string | undefined
			};
			
			console.log('Sending payload:', payload);
			
			return payload;
			},
		invalidateAll: false,
		validators: zodClient(contentCreateSchema),
		dataType: 'json',
		onResult({ result }) {
			if (result.type === 'success') {
				invalidate('data:feed').then(() => {
					history.back();
				});
			} else if (result.type === 'error') {
				console.error('Form validation errors:', result.error);
			}
		}
	});

	const { form, errors, enhance, delayed, allErrors, validate } = superform;

	const searchparams = queryParameters({ circles: ssp.array() });
	if ($searchparams.circles) $form.circles = $searchparams.circles;

	$: $form.text = DEFAULT_EDITOR_TXT;
	$: $form.title = contentTitle;

	//@ts-ignore
	function handleMentionsChange(e) {
		mentions = e.detail;
		console.log('Mentions aktualisiert in ContentInput:', mentions);
	}

	$: $form.mentions = mentions;


	function closeModal() {
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
            bind:readonly
            on:mentionsChange={handleMentionsChange}
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
        {#if Array.isArray($errors.mentions) && $errors.mentions.length > 0}<span class="text-error-500">{$errors.mentions.join(", ")}</span>{/if}
        <FileUpload {superform} />
        {#if $form?.files?.length > 0}
            <div class="flex items-center gap-2 mb-4">
                <input
                type="checkbox"
                name="to_be_parsed_by_directus_flow"
                bind:checked={$form.to_be_parsed_by_directus_flow}
                class="input checkbox h-4 w-4"
            /> 
                <span class="text-sm">Dokument als Text posten</span>
            </div>
        {/if}
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

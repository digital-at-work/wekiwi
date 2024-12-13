<script lang="ts">
	import { page } from '$app/stores';

	import { createEventDispatcher } from 'svelte';

	import { route } from '$lib/ROUTES';

	import { DEFAULT_EDITOR_TXT, DEFAULT_EDITOR_TXT1 } from '$lib/config/constants';
	import Editor from '$lib/components/editor/Editor.svelte';

	import type { Infer } from 'sveltekit-superforms';
	import { superForm } from 'sveltekit-superforms';
	import { zodClient } from 'sveltekit-superforms/adapters';
	import { contentCreateSchema } from '$lib/config/zod-schemas';

	import { SendHorizontal, X } from 'lucide-svelte';

	import type { PartialUser } from '$lib/directus/directus.types';

	import { ConicGradient } from '@skeletonlabs/skeleton';
	import FileUpload from '$lib/components/ui/forms/FileUpload.svelte';

	//import { getStateContext } from '$lib/state';

	export let readonly = false;

	export let parent_id: string | undefined;
	export let parent_circles: number[] | undefined;
	export let circleUsers: Promise<PartialUser[]>;
	export let contentCreateForm;

	//const { modifyContent } = getStateContext();

	const dispatch = createEventDispatcher();

	const superform = superForm<Infer<typeof contentCreateSchema>>(contentCreateForm, {
		invalidateAll: false,
		validators: zodClient(contentCreateSchema),
		onSubmit: async ({ formData }) => {
			formData.set('text', (formData.get('text') as string));
		},
		onResult({ result }) {
			if (result.type === 'success') {
				//modifyContent(result.data?.content.content_id, { ...result.data?.content, text: $form.text, title: $form.title }, Number(parent_id), 'add');
				dispatch('subContentInput', {
					...result.data?.content,
					text: $form.text,
					title: $form.title
				});
			}
		},
		onUpdated() {
			$form.circles = parent_circles as number[];
		}
	});

	const { form, errors, enhance, delayed, allErrors, validate } = superform;

	$form.text = DEFAULT_EDITOR_TXT;
	$form.circles = parent_circles as number[];

	let content_type: string = 'text';
</script>

<div class="grid grid-rows-[auto_1fr_auto]">
	<form
		method="POST"
		enctype="multipart/form-data"
		action={route('createContent /app/content_create', {
			c_id: $page.data.user?.company_id,
			parent_id: parent_id,
			type: content_type
		})}
		use:enhance
	>
		<div class="page-section">
			<!-- TODO: possibility to choose type -->
			<div class="mt-6 rounded-lg border-2 p-4">
				{#await circleUsers}
					Loading...
				{:then circleUsers}
					<Editor
						placeholder={DEFAULT_EDITOR_TXT1}
						inline={true}
						cssClasses="tinymce-wrapper *:rounded-lg *:min-h-24 *:border-solid *:border-2 p-2"
						{circleUsers}
						bind:htmlContent={$form.text}
						bind:mentions={$form.mentions}
						bind:readonly
						on:input={() => validate('text')}
					/>
					<input type="hidden" name="text" bind:value={$form.text} />
					<input type="hidden" name="mentions" bind:value={$form.mentions} />
					<input type="hidden" name="circles" bind:value={$form.circles} />
				{:catch error}
					<p class="text-error-500">{error.message}</p>
				{/await}
			</div>

			{#if $errors.text}<span class="text-error-500">{$errors.text}</span>{/if}
			{#if $errors.mentions?._errors}<span class="text-error-500">{$errors.mentions?._errors}</span
				>{/if}

			<FileUpload {superform} />

			<hr />

			<div class="flex items-center justify-end">
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
						<span>Antworten</span>
						<span><SendHorizontal /></span>
					{/if}
				</button>
			</div>
		</div>
	</form>
</div>

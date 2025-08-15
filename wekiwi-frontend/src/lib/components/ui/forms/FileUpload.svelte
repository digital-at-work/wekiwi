<script lang="ts">
	import { UploadCloud, X } from 'lucide-svelte';

	import { FileDropzone } from '@skeletonlabs/skeleton';
	import { Check } from 'lucide-svelte';

	import { superForm } from 'sveltekit-superforms';
	import { contentCreateSchema } from '$lib/config/zod-schemas';

	export let superform;

	const { errors, form } = superform;

	let fileinput: HTMLInputElement;

	function handleFileChange(e: Event) {
		const input = e.currentTarget as HTMLInputElement;
		if (!input || !input.files) return;

		const newFiles: File[] = Array.from(input.files);
		const existingFiles: File[] = $form.files || [];

		const combined: File[] = [
			...existingFiles,
			...newFiles.filter(
				(f: File) => !existingFiles.some((ef: File) => ef.name === f.name && ef.size === f.size)
			)
		];

		const dt = new DataTransfer();
		combined.forEach((file) => dt.items.add(file));
		input.files = dt.files;

		$form.files = combined;
	}
</script>

<div>
	<FileDropzone
		name="files"
		id="files"
		type="file"
		accept=".pdf,.jpg,.jpeg,.png"
		padding="{!!$form?.files.length
			? 'btn variant-filled-primary'
			: 'variant-soft-secondary'} h-10 w-full border-surface-500 hover:border-primary-500"
		multiple
		on:change={handleFileChange}
		bind:fileInput={fileinput}
	>
		<svelte:fragment slot="message">
			<div class="flex items-center">
				<UploadCloud />
				<span class="ml-2">Dokument hochladen</span>
			</div>
		</svelte:fragment>
	</FileDropzone>

	<hr />

	<div class="flex flex-wrap gap-0.5">
		{#each Array.from(fileinput?.files || []) as file, index (file)}
			<div>
				<button
					class="variant-filled chip hover:variant-soft"
					on:click={() => {
						// Remove the file
						// @ts-ignore
						const newFiles = Array.from(fileinput.files).filter((f) => f.name !== file.name);

						// Create a new DataTransfer object
						const dt = new DataTransfer();
						newFiles.forEach((file) => dt.items.add(file));

						$form.files = newFiles;
						fileinput.value = '';
						fileinput.files = dt.files;
					}}
				>
					<div class="flex items-center gap-2">
						<span>{file.name}</span>
						<span><X color="red" /></span>
					</div>
				</button>
				{#if $errors && Array.isArray($errors.files) && $errors.files[index]}
					<span class="text-error-500">{$errors.files[index]}</span>
				{/if}
			</div>
		{/each}
	</div>
</div>

<!-- {#if $form?.files?.length > 0}
	<div class="mt-2 flex items-center">
		<span class="text-sm">Dokument analysieren</span>
	</div>
{/if} -->

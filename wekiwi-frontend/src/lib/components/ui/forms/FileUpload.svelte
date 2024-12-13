<script lang="ts">
	import { UploadCloud, X } from 'lucide-svelte';

	import { FileDropzone } from '@skeletonlabs/skeleton';

	export let superform;

	const { errors, form } = superform;

	let fileinput: HTMLInputElement;
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
		on:change={(e) => {
			// @ts-ignore
			$form.files = Array.from(e.currentTarget.files ?? []);
		}}
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
					<span>{file.name}</span>
					<span><X color="red" /></span>
				</button>
				{#if $errors && $errors[`${index}`]}
					<span class="text-error-500">{$errors[`${index}`]}</span>
				{/if}
			</div>
		{/each}
	</div>
</div>

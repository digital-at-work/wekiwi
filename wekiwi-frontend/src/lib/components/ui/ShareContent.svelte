<script lang="ts">
	import { page } from '$app/stores';

	import { superForm } from 'sveltekit-superforms';
	import { zod } from 'sveltekit-superforms/adapters';
	import { contentShareSchema } from '$lib/config/zod-schemas';

	import { InputChip, clipboard, ConicGradient, Autocomplete } from '@skeletonlabs/skeleton';
	import type { ConicStop, AutocompleteOption } from '@skeletonlabs/skeleton';

	import { route } from '$lib/ROUTES';

	export let content_id: number;
	export let shareContentForm;

	const { form, errors, enhance, delayed } = superForm(shareContentForm, {
		validators: zod(contentShareSchema),
		resetForm: false,
		clearOnSubmit: 'none'
	});

	const conicStops: ConicStop[] = [
		{ color: 'transparent', start: 0, end: 25 },
		{ color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
	];

	let autocompleteInput = '';
	let userSuggestions: AutocompleteOption<string>[] = [];

	$page.data.circleUsers.then(
		(users: { username: string; first_name: string; last_name: string }[]) => {
			userSuggestions = users.map((user: any) => ({
				keywords: `${user.username}, ${user.first_name}, ${user.last_name}`,
				label: user.username,
				value: user.username
			}));
		}
	);

</script>

<h2>Share Content</h2>
<form
	method="POST"
	action={route('shareContent /app/[content_id=integer]', {
		content_id: content_id.toString()
	})}
	use:enhance
>
	<button use:clipboard={$page.url.toString()}>Link kopieren</button>
	<label for="emails">Emails:</label>
	<InputChip bind:value={$form.emails} name="emails" placeholder="Gebe Emails ein..." />
	{#if $errors.emails}
		<p class="error">{$errors.emails}</p>
	{/if}

	<label for="usernames">Nutzernamen:</label>
	<InputChip bind:value={$form.usernames} name="usernames" placeholder="Gebe Nutzernamen ein..." />
	<div class="card max-h-48 w-full max-w-sm overflow-y-auto p-4" tabindex="-1">
		<Autocomplete
			bind:input={autocompleteInput}
			options={userSuggestions}
			on:selection={(e) => {
				$form.usernames = [...$form.usernames, e.detail.value];
			}}
		/>
	</div>
	{#if $errors.usernames}
		<p class="error">{$errors.usernames}</p>
	{/if}

	<label for="dateEnd">Ablaufdatum (optional):</label>
	<input type="date" bind:value={$form.dateEnd} name="dateEnd" />
	{#if $errors.date_end}
		<p class="error">{$errors.date_end}</p>
	{/if}

	<label for="maxUses">Maximale Anzahl Zugriffe (optional):</label>
	<input type="number" bind:value={$form.maxUses} name="maxUses" />
	{#if $errors.maxUses}
		<p class="error">{$errors.maxUses}</p>
	{/if}

	<label for="password">Passwort (optional):</label>
	<input type="password" bind:value={$form.password} name="password" />
	{#if $errors.password}
		<p class="error">{$errors.password}</p>
	{/if}

	<button type="submit">
		{#if $delayed}
			<ConicGradient stops={conicStops} spin width="w-6" />
		{:else}
			Teilen
		{/if}
	</button>
</form>

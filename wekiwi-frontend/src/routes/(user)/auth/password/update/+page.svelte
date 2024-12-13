<script lang="ts">
	import type { PageData } from './$types';

	import { ConicGradient } from '@skeletonlabs/skeleton';
	import type { ConicStop } from '@skeletonlabs/skeleton';

	import { superForm } from 'sveltekit-superforms';
	import { userUpdatePasswordSchema } from '$lib/config/zod-schemas';
	import { zodClient } from 'sveltekit-superforms/adapters';

	import { AlertTriangle } from 'lucide-svelte';

	export let data: PageData;

	const { form, errors, enhance, delayed } = superForm(data.form, {
		validators: zodClient(userUpdatePasswordSchema),
		delayMs: 0
	});

	const conicStops: ConicStop[] = [
		{ color: 'transparent', start: 0, end: 25 },
		{ color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
	];
</script>

<form method="POST" use:enhance>
	{#if $errors._errors}
		<aside class="alert variant-filled-error mt-6">
			<div><AlertTriangle size="42" /></div>
			<div class="alert-message">
				<h3 class="h3">Problem beim der Passwortzurücksetzung</h3>
				<p>{$errors._errors}</p>
			</div>
		</aside>
	{/if}

	<h3>Wähle Dein neues Passwort:</h3>

	<hr class="mb-6 mt-2 !border-t-2" />

	<div class="mt-6">
		<label class="label">
			<span class="sr-only">Neues Passwort</span>
			<input
				id="password"
				name="password"
				type="password"
				placeholder="Neues Passwort"
				data-invalid={$errors.password}
				bind:value={$form.password}
				class="input {$errors.password ? 'input-error' : ''}"
			/>
			{#if $errors.password}
				<small>{$errors.password}</small>
			{/if}
		</label>
	</div>

	<div class="mt-6">
		<label class="label">
			<span class="sr-only">Neues Passwort bestätigen</span>
			<input
				id="confirmPassword"
				name="confirmPassword"
				type="password"
				placeholder="Neues Passwort"
				data-invalid={$errors.confirmPassword}
				bind:value={$form.confirmPassword}
				class="input {$errors.confirmPassword ? 'input-error' : ''}"
			/>
			{#if $errors.confirmPassword}
				<small>{$errors.confirmPassword}</small>
			{/if}
		</label>
	</div>

	<div class="mt-6">
		<button type="submit" class="variant-filled-primary btn w-full">
			{#if $delayed}
				<ConicGradient stops={conicStops} spin width="w-6" />
			{:else}
				Passwort zurücksetzen
			{/if}
		</button>
	</div>
</form>

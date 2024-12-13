<script lang="ts">
	import { route } from '$lib/ROUTES';

	import { ConicGradient } from '@skeletonlabs/skeleton';
	import type { ConicStop } from '@skeletonlabs/skeleton';

	import { superForm } from 'sveltekit-superforms';
	import { signInSchema } from '$lib/config/zod-schemas';
	import { zodClient } from 'sveltekit-superforms/adapters';

	import { AlertTriangle } from 'lucide-svelte';

	import { getDirectusClient } from '$lib/directus/directus';


	export let data;

	const DirectusClient = getDirectusClient();	

	const { form, errors, enhance, delayed } = superForm(data.form, {
		validators: zodClient(signInSchema),
		onSubmit: ({ formData, cancel }) => {
			const email = formData.get('email') as string;
			const password = formData.get('password') as string;
			
			try {
				// Login with Directus on client with session cookie set for the main domain
				DirectusClient.login(email, password);
			} catch (err: any) {
				// Handle error and cancel submission
				$errors._errors?.push(err.errors[0].message);
				cancel();
			}
		}
	});

	const conicStops: ConicStop[] = [
		{ color: 'transparent', start: 0, end: 25 },
		{ color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
	];
</script>

<form method="POST" action={route('default /auth/sign-in')} use:enhance>
	
	{#if $errors._errors}
		<aside class="alert variant-filled-error mt-6">
			<div><AlertTriangle size="42" /></div>
			<div class="alert-message">
				<h3 class="h3">Problem beim Anmelden</h3>
				<p>{$errors._errors}</p>
			</div>
		</aside>
	{/if}

	<div class="mt-6">
		<label class="label">
			<span class="sr-only">E-Mail</span>
			<input
				id="email"
				name="email"
				type="email"
				placeholder="E-Mail"
				autocomplete="email"
				data-invalid={$errors.email}
				bind:value={$form.email}
				class="input"
				class:input-error={$errors.email}
			/>
			{#if $errors.email}
				<small>{$errors.email}</small>
			{/if}
		</label>
	</div>

	<div class="mt-6">
		<label class="label">
			<span class="sr-only">Passwort</span>
			<input
				id="password"
				name="password"
				type="password"
				placeholder="Passwort"
				data-invalid={$errors.password}
				bind:value={$form.password}
				class="input"
				class:input-error={$errors.password}
			/>
			{#if $errors.password}
				<small>{$errors.password}</small>
			{/if}
		</label>
	</div>

	<div class="mt-6">
		<button type="submit" class="btn variant-filled-primary w-full">
			{#if $delayed}
				<ConicGradient stops={conicStops} spin width="w-6" />
			{:else}
				Anmelden
			{/if}
		</button>
	</div>
	
	<div class="mt-8 text-center">
		<a href={route('/auth/password/reset')}>Passwort vergessen?</a>
	</div>
</form>

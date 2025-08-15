<script lang="ts">
	import { page } from '$app/stores';
	import { route } from '$lib/ROUTES';

	import { superForm } from 'sveltekit-superforms';
	import { signUpSchema } from '$lib/config/zod-schemas';
	import { zodClient } from 'sveltekit-superforms/adapters';

	import { ConicGradient } from '@skeletonlabs/skeleton';
	import type { ConicStop } from '@skeletonlabs/skeleton';

	import { AlertTriangle } from 'lucide-svelte';

	interface PasswordRequirements {
		length: boolean;
		uppercase: boolean;
		lowercase: boolean;
		number: boolean;
		special: boolean;
	}

	export let data;

	let password = '';

	function checkPasswordRequirements(password: string): PasswordRequirements {
		return {
			length: password.length >= 10,
			uppercase: /[A-Z]/.test(password),
			lowercase: /[a-z]/.test(password),
			number: /\d/.test(password),
			special: /[\W_]/.test(password)
		};
	}

	const { form, errors, enhance, delayed } = superForm(data.form, {
		validators: zodClient(signUpSchema),
		delayMs: 0,
		onResult: (result) => {
			console.log('result', result);
		}
	});

	const conicStops: ConicStop[] = [
		{ color: 'transparent', start: 0, end: 25 },
		{ color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
	];

	function isPasswordValid(password: string): boolean {
		const requirements = checkPasswordRequirements(password);
		return (
			requirements.length &&
			requirements.uppercase &&
			requirements.lowercase &&
			requirements.number &&
			requirements.special
		);
	}

	$: isFormValid = $form.terms && password && isPasswordValid(password);

	$: $form.password && (password = $form.password);

	function getIsFormValid(): boolean {
		return isFormValid;
	}
</script>

{#if $page.url.searchParams.get('circles')}
	<div class="mb-6">
		Du wurdest eingeladen. Bitte registriere dich, um teil von Wekiwi zu werden.
	</div>
{/if}

<form method="POST" action={route('signUp /auth/sign-up')} use:enhance>
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
			<span class="sr-only">Username</span>
			<input
				id="username"
				name="username"
				type="text"
				placeholder="Username"
				autocomplete="given-name"
				data-invalid={$errors.username}
				bind:value={$form.username}
				class="input"
				class:input-error={$errors.username}
			/>
			{#if $errors.username}
				<small>{$errors.username}</small>
			{/if}
		</label>
	</div>

	<div class="mt-6">
		<label class="label">
			<span class="sr-only">Vorname</span>
			<input
				id="first_name"
				name="first_name"
				type="text"
				placeholder="Vorname"
				autocomplete="given-name"
				data-invalid={$errors.first_name}
				bind:value={$form.first_name}
				class="input"
				class:input-error={$errors.first_name}
			/>
			{#if $errors.first_name}
				<small>{$errors.first_name}</small>
			{/if}
		</label>
	</div>

	<div class="mt-6">
		<label class="label">
			<span class="sr-only">Nachname</span>
			<input
				id="last_name"
				name="last_name"
				type="text"
				placeholder="Nachname"
				autocomplete="family-name"
				data-invalid={$errors.last_name}
				bind:value={$form.last_name}
				class="input"
				class:input-error={$errors.last_name}
			/>
			{#if $errors.last_name}
				<small>{$errors.last_name}</small>
			{/if}
		</label>
	</div>

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
			<div class="password-requirements mt-2">
				<div
					class="requirement"
					style="color: {checkPasswordRequirements($form.password).length ? 'green' : 'red'}"
				>
					✓ Mindestens 10 Zeichen
				</div>
				<div
					class="requirement"
					style="color: {checkPasswordRequirements(password).uppercase ? 'green' : 'red'}"
				>
					✓ Mindestens ein Großbuchstabe
				</div>
				<div
					class="requirement"
					style="color: {checkPasswordRequirements(password).number ? 'green' : 'red'}"
				>
					✓ Mindestens eine Nummer
				</div>
				<div
					class="requirement"
					style="color: {checkPasswordRequirements(password).special ? 'green' : 'red'}"
				>
					✓ Mindestens ein Sonderzeichen
				</div>
			</div>
			{#if $errors.password}
				<small>{$errors.password}</small>
			{/if}
		</label>
	</div>
	<div class="mt-6">
		<label for="terms" class="flex items-center space-x-4">
			<input id="terms" name="terms" type="checkbox" class="checkbox" bind:checked={$form.terms} />
			<p>
				Ich akzeptiere die
				<a href={route('/imprint/termsofuse')} class="text-primaryHover underline"
					>Auftragsverarbeitungsvereinbarung</a
				>
				und
				<a href={route('/imprint/privacypolicy')} class="text-primaryHover underline"
					>Datenschutzbestimmungen</a
				>
			</p>
		</label>
	</div>

	{#if $errors.terms}
		<small>{$errors.terms}</small>
	{/if}

	<div class="mt-6">
		<button
			type="submit"
			disabled={!isFormValid}
			class="btn variant-filled-primary w-full"
		>
			{#if $delayed}<ConicGradient stops={conicStops} spin width="w-6" />{:else}Anmelden{/if}
		</button>
	</div>
</form>

<style>
	.password-requirements {
		margin-top: 1rem;
	}
	.requirement {
		font-size: 0.9rem;
		margin: 0.25rem 0;
	}
</style>

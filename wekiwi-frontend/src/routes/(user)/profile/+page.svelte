<script lang="ts">
	import { route } from '$lib/ROUTES.js';

	import { superForm } from 'sveltekit-superforms';
	import { profileSchema } from '$lib/config/zod-schemas';
	import { zodClient } from 'sveltekit-superforms/adapters';

	import { ConicGradient } from '@skeletonlabs/skeleton';
	import type { ConicStop } from '@skeletonlabs/skeleton';

	import { DEFAULT_PLACEHOLDER_AVATAR } from '$lib/config/constants';

	export let data;

	const { form, errors, enhance, delayed } = superForm(data.form, {
		validators: zodClient(profileSchema),
		delayMs: 0
	});

	const conicStops: ConicStop[] = [
		{ color: 'transparent', start: 0, end: 25 },
		{ color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
	];

	let editing = false;
</script>

<svelte:head>
	<title>Benutzerprofil</title>
</svelte:head>

<div class="container mx-auto">
	<form method="POST" action={route('save /profile')} use:enhance>
		<button type="button" on:click={() => (editing = !editing)} class="variant-filled btn">
			Bearbeiten
		</button>

		<div class="relative mb-8">
			<img
				src={($form.avatar && URL.createObjectURL($form.avatar)) ||
					DEFAULT_PLACEHOLDER_AVATAR + data.user?.username}
				alt="user avatar"
				class="max-h-fit rounded-t-md shadow-md"
			/>
			<button
				type="button"
				on:click={() => (editing = !editing)}
				class="variant-filled btn absolute bottom-4 right-4 w-28 font-semibold"
			>
				Bearbeiten
			</button>
		</div>

		<label class="label mb-6 flex items-end gap-4">
			<span>Profilbild</span>
			<input
				class="input"
				type="file"
				name="profile_image"
				bind:value={$form.avatar}
				disabled={!editing}
			/>
		</label>

		{#if $errors.avatar}
			<small class="error">{$errors.avatar}</small>
		{/if}

		<div class="p-6 pb-8">
			<div class="mb-4">
				<label class="label flex items-end gap-4">
					<span>Username</span>
					<input
						class="input {$errors.username ? 'input-error' : ''}"
						type="text"
						name="username"
						placeholder="Username"
						bind:value={$form.username}
						disabled={!editing}
					/>
				</label>
				{#if $errors.username}
					<small class="error">{$errors.username}</small>
				{/if}
			</div>

			<label class="label mb-4 flex items-end gap-4">
				<span>Email</span>
				<input
					class="input {$errors.email ? 'input-error' : ''}"
					type="email"
					name="email"
					placeholder="Email"
					bind:value={$form.email}
					disabled={!editing}
				/>
				{#if $errors.email}
					<small class="error">{$errors.email}</small>
				{/if}
			</label>

			<label class="label mb-4 flex items-start gap-4">
				<span>Biografie</span>
				<textarea
					class="textarea"
					rows="4"
					placeholder="Kurze Biografie über Sie"
					bind:value={$form.bio}
					disabled={!editing}
				/>
			</label>

			<div class="mx-auto mt-6 w-2/3">
				<button type="submit" disabled={!editing} class="variant-filled-primary btn w-full">
					{#if $delayed}
						<ConicGradient stops={conicStops} spin width="w-6" />
					{:else}
						Profil aktualisieren
					{/if}
				</button>
			</div>
		</div>
	</form>
</div>

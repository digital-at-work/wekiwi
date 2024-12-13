<script lang="ts">
	import { route } from '$lib/ROUTES';

	import { superForm } from 'sveltekit-superforms';
	import { inviteSchema } from '$lib/config/zod-schemas';
	import { zodClient } from 'sveltekit-superforms/adapters';

	import { ConicGradient } from '@skeletonlabs/skeleton';
	import type { ConicStop } from '@skeletonlabs/skeleton';

	export let data;

	const { form, errors, enhance, delayed } = superForm(data.form, {
		validators: zodClient(inviteSchema),
		delayMs: 0
	});

	const conicStops: ConicStop[] = [
		{ color: 'transparent', start: 0, end: 25 },
		{ color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
	];
</script>

<form method="POST" action={route('default /app/admin/invite')} use:enhance>
	<div class="mt-6">
		<label class="label">
			<span class="sr-only">E-Mail des Empfängers</span>
			<input
				id="recipientEmail"
				name="recipientEmail"
				type="email"
				placeholder="E-Mail des Empfängers"
				autocomplete="email"
				data-invalid={$errors.recipientEmail}
				class="input"
				class:input-error={$errors.recipientEmail}
				bind:value={$form.recipientEmail}
			/>
			{#if $errors.recipientEmail}
				<small>{$errors.recipientEmail}</small>
			{/if}
		</label>
	</div>
	<!-- <div class="mt-6">
        <label class="label">
            <span class="sr-only">Ihre Nachricht</span>
            <textarea
                id="message"
                name="message"
                placeholder="Ihre Nachricht (optional)"
                data-invalid={$errors.message}
                bind:value={$form.message}
                class="textarea"
                class:textarea-error={$errors.message}
            ></textarea>
            {#if $errors.message}
                <small>{$errors.message}</small>
            {/if}
        </label>
    </div> -->
	{#each data.user?.circles ?? [] as circle, i}
		<div class="flex items-center px-4 py-2">
			<input
				id={circle?.id}
				type="checkbox"
				class="h-4 w-4 rounded"
				bind:value={$form.circles[i].circle_id}
			/>
			<label for={circle?.id} class="ml-2 block text-sm">{circle?.name}</label>
		</div>

		<label for="role" class="block text-sm">Role</label>
		<!-- <select id={circle?.role} name="role" class="" bind:value={$form.circles[i].role}>
			<option value="Circle Benutzer">Circle Benutzer</option>
			<option value="Circle Admin">Circle Admin</option>
		</select> -->

		{#if $errors.circles?._errors}
			{#each $errors.circles?._errors as error}
				<p class="mt-2 text-sm text-red-600">{error}</p>
			{/each}
		{/if}
	{/each}

	<div class="mt-6">
		<button type="submit" class="variant-filled-primary btn w-full">
			{#if $delayed}
				<ConicGradient stops={conicStops} spin width="w-6" />
			{:else}
				Einladung senden
			{/if}
		</button>
	</div>
</form>

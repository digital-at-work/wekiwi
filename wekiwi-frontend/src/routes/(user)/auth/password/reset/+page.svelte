<script lang="ts">
    import { ConicGradient } from '@skeletonlabs/skeleton';
    import type { ConicStop } from '@skeletonlabs/skeleton';

    import { superForm } from 'sveltekit-superforms';
    import { resetPasswordSchema } from '$lib/config/zod-schemas';
    import { zodClient } from 'sveltekit-superforms/adapters';

    import { AlertTriangle } from 'lucide-svelte';
    
    export let data;

    const { form, errors, enhance, delayed } = superForm(data.form, {
        validators: zodClient(resetPasswordSchema),
        delayMs: 0
    });

    const conicStops: ConicStop[] = [
        { color: 'transparent', start: 0, end: 25 },
        { color: 'rgb(var(--color-primary-900))', start: 75, end: 100 }
    ];

</script>

<h3>Ihr Passwort zurücksetzen</h3>

<hr class="!border-t-2 mt-2 mb-6" />

<form method="POST" use:enhance>
    {#if $errors._errors}
        <aside class="alert variant-filled-error mt-6">
            <div><AlertTriangle size="42" /></div>
            <div class="alert-message">
                <h3 class="h3">Problem bei Passwortrücksetzung</h3>
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
                placeholder="E-Mail-Adresse"
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
        <button type="submit" class="btn variant-filled-primary w-full">
            {#if $delayed}
                <ConicGradient stops={conicStops} spin width="w-6" />
            {:else}
                E-Mail zum Zurücksetzen senden
            {/if}
        </button>
    </div>
</form>

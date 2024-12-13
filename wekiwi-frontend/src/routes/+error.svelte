<script>
    import { page } from '$app/stores';
    import ListErrors from '$lib/components/ListErrors.svelte';
</script>

<svelte:head>
    <title>We:KiWi - Error: {$page.status}</title>
</svelte:head>

<div class="flex flex-col items-center justify-center h-screen bg-gray-100 text-gray-800">
    {#if $page.status === 404}
        <h1 class="text-4xl md:text-6xl font-bold">Inhalt nicht gefunden!</h1>
        <p class="mt-3 text-lg md:text-xl">Die von dir gesuchte Seite existiert nicht oder wurde verschoben.</p>
    {:else}
        <h1 class="text-4xl md:text-6xl font-bold">Ups... da ist etwas schief gelaufen</h1>
        <ListErrors errors={$page.error}/>
    {/if}
    <a href="/" class="p-8 text-white rounded text-primary-500 hover:bg-surface-700 transition duration-300">Zurück zur Startseite</a>
</div>

<script lang="ts">

    import { UserRoundX } from 'lucide-svelte';

</script>

<svelte:head>
	<title>Verizifierung • WeKiwi</title>
</svelte:head>

<div class="flex flex-col items-center justify-center h-screen">
    <div class="p-4">
        <UserRoundX />
    </div>
        <h1 class="text-xl md:text-2xl font-bold">Leider ist bei der Verifizierung etwas schiefgelaufen.</h1>
        <p class="mt-3 text-md md:text-lg">Bitte versuche es später nocheinmal.</p>
    <a href="/" class="mt-5 px-4 py-2 rounded hover:bg-surface-700 transition duration-300">Zurück zur Startseite</a>
</div>

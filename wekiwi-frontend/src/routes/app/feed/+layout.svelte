<script lang="ts">
	import { fade } from 'svelte/transition';

	import SidebarLeft from '$lib/components/ui/nav/SidebarLeft.svelte';

	import { Filter } from 'lucide-svelte';

	import { getDrawerStore } from '@skeletonlabs/skeleton';

	export let data;

	const drawerStore = getDrawerStore();
</script>

<svelte:head>
	<title>Wekiwi - Feed</title>
</svelte:head>

<div class="flex flex-col md:flex-row">
	{#if $drawerStore.open === true}
		<aside
			in:fade={{ duration: 260 }}
			out:fade={{ duration: 180 }}
			class="sticky top-0 z-20 m-2 rounded-lg md:h-96 md:w-60"
		>
			<SidebarLeft usersCircles={data.user?.circles} circleUsers={data?.circleUsers} />
		</aside>
	{/if}
	<button
		on:click={() => ($drawerStore.open === true ? drawerStore.close() : drawerStore.open())}
		class="variant-filled-primary chip z-20 m-2 h-10 py-2 hover:variant-filled-secondary"
	>
		<span><Filter /></span>
	</button>

	<div class="fixed h-screen w-screen">
		<slot />
	</div>
</div>

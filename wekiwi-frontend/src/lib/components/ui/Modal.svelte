<script lang="ts">
	import { trapfocus } from '$lib/utils';
	import { createEventDispatcher } from 'svelte';
	import { fade, scale } from 'svelte/transition';

	import { X } from 'lucide-svelte';

	export let blur: boolean = true;
	export let location: string = 'justify-center';

	const dispatch = createEventDispatcher();

	function closeModal() {
		if (window.tinymce) {
			window.tinymce.remove();
			console.log('TinyMCE instances removed');
		}
		dispatch('close');
	}

</script>

<svelte:window
	on:keydown={(e) => {
		if (e.key === 'Escape') {
			dispatch('close');
		}
	}}
/>

<div
	class="backdrop-grayscale-50 fixed left-0 z-30 h-screen w-screen"
	class:backdrop-blur-sm={blur}
	use:trapfocus
	transition:fade={{ duration: 100 }}
>
	<!-- svelte-ignore a11y-click-events-have-key-events-->
	<div
		class="flex h-screen w-screen items-center {location} overflow-hidden"
		role="button"
		tabindex="0"
		transition:scale={{ start: 0.95, duration: 100 }}
		on:click={(e) => {
			if (e.target === e.currentTarget) {
				closeModal();
			}
		}}
	>
		<div class="relative overflow-y-auto" style="max-height: calc(100vh - 60px);">
			<button
				class="variant-filled-primary btn btn-sm absolute right-14 top-14 ml-14"
				on:click={closeModal}
			>
				<X />
			</button>
			<div class="h-full overflow-y-auto">
				<slot />
			</div>
		</div>
	</div>
</div>

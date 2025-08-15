<script lang="ts">
	import { invalidate } from '$app/navigation';
	import { navigating } from '$app/stores';

	import { onMount } from 'svelte';

	import FeedPreviewContainer from '$lib/components/content/feed/FeedPreviewContainer.svelte';
	import { getStateContext } from '$lib/state';

	export let data;

	const { initContents, addContents, contents } = getStateContext();

	let container: FeedPreviewContainer;

	let can_restore = false;
	onMount(() => {
		invalidate('data:feed');
	});
	$: if ($navigating) {
		// check if back or forward button in browser was clicked
		can_restore = $navigating.type === 'popstate';
	}

	export const snapshot = {
		capture: () => ({
			contents: $contents,
			scroller: container?.capture(),

			// TODO: Push state to directus for presistance?
		}),
		restore: (values) => {
			if (!can_restore) return;

			data.contents = values.contents;

			if (values.scroller) {
				container.restore(values.scroller);
			}
		}
	};

	// First page comes from the server
	let offset: number;

	$: {
		initContents(data.contents);
		offset = data.contents.length
	}
</script>

<!-- TODO: styling messed up here... the feed should have padding and define the space between the items -->
<FeedPreviewContainer
	contents={$contents}
	bind:this={container}
	{offset}
	on:loaded={(e) => {
		offset += e.detail.newContents.length;
		addContents(e.detail.newContents);

		console.debug('AFTER UPDATE', $contents);
	}}
>
	<p slot="empty" class="h4 p-10 text-center">Noch keine Inhalte in diesem Circle.</p>
</FeedPreviewContainer>

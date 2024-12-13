<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	import { route } from '$lib/ROUTES';

	import FeedContentPreview from '$lib/components/content/feed/FeedContentPreview.svelte';
	import FeedPreviewPlaceholder from '$lib/components/content/feed/FeedPreviewPlaceholder.svelte';

	import Scroller from '$lib/components/content/feed/Scroller.svelte';

	import { readItems } from '@directus/sdk';
	import type { PartialContents } from '$lib/directus/directus.types';
	import { requestContents, requestVectorContents } from '$lib/directus/requests.js';

	import { getDirectusClientProxy } from '$lib/directus/directus';

	import { queryParameters, ssp } from 'sveltekit-search-params';

	import { FEED_CHECKMORE_TIMEOUT } from '$lib/config/constants';

	const params = queryParameters({
		ai: ssp.boolean(),
		circles: ssp.array()
	});

	export let contents: PartialContents;
	export let offset: number | undefined;

	export function capture() {
		return scroller.capture();
	}

	export function restore(values: any) {
		scroller.restore(values);
	}

	const dispatch = createEventDispatcher();

	const directusProxyClient = getDirectusClientProxy();

	let scroller: Scroller;
	
	let loading = false;
	let checkMore = true;
</script>

<Scroller
	bind:this={scroller}
	items={contents}
	on:more={async () => {
		if (loading || !checkMore) return;
		loading = true;

		console.log('LOADING... Offset:', offset);

		const newContents = (!$params.ai || $params.search.trim().length === 0)
			? await directusProxyClient.request(
					readItems(
						'contents',
						// @ts-ignore
						requestContents(
							$params.type || 'text',
							$params.circles || [],
							$params.search || '',
							$params.c_id || '',
							$params.sort1 || '',
							$params.sort2 || '',
							$params.usercreated || '',
							$params.userupdated || '',
							$params.datecreated1 || '',
							$params.datelogic1 || '',
							$params.datecreated2 || '',
							$params.dateupdated1 || '',
							$params.datelogic2 || '',
							$params.dateupdated2 || '',
							offset
						)
					)
				)
			: await fetch(route('ai_proxy', { ai_slug: '/v1/content/search' }), {
					method: 'POST',
					headers: {
						accept: 'application/json',
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(
						requestVectorContents(
							$params.type || 'text',
							$params.circles || [],
							$params.search || '',
							$params.c_id || '',
							$params.usercreated || '',
							$params.userupdated || '',
							$params.datecreated1 || '',
							$params.datelogic1 || '',
							$params.datecreated2 || '',
							$params.dateupdated1 || '',
							$params.datelogic2 || '',
							$params.dateupdated2 || '',
							offset
						)
					)
				}).then((res) => res.json());

		if (newContents.length === 0) {
			checkMore = false;
			setTimeout(() => {
				checkMore = true;
			}, FEED_CHECKMORE_TIMEOUT);
			loading = false;
			return;
		}

		dispatch('loaded', {
			newContents: newContents,
		});
		
		loading = false;
	}}
>
	<div slot="item" class="mx-auto max-w-2xl mt-4" let:item>
		<div class="py-8">
			<div class="block">
				<FeedContentPreview content={item} />
			</div>
		</div>
	</div>

	<div slot="empty">
		<slot name="empty" />
	</div>

	<div slot="footer" class="mx-auto max-w-2xl mb-16">
		{#if loading}
		    <!-- TODO: needs to have delay on removal, feed loads too quickly to notice loading event -->
			<FeedPreviewPlaceholder />
		{/if}
	</div>
</Scroller>

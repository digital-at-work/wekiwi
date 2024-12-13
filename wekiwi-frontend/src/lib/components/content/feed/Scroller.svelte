<script lang="ts">
	import { createEventDispatcher, onMount, tick } from 'svelte';
	import type { PartialContents } from '$lib/directus/directus.types';

	import { FEED_BUTTOM_THRESHOLD_LOADMORE_PX } from '$lib/config/constants';

	export let items: PartialContents;

	export function capture() {
		const scroll = scroller.scrollTop;
		return { a, b, top, bottom, heights, scroll };
	}

	export async function restore(state: {
		a: number;
		b: number;
		top: number;
		bottom: number;
		heights: number[];
		scroll: number;
	}) {
		a = state.a;
		b = state.b;
		top = state.top;
		bottom = state.bottom;
		heights = state.heights;

		await tick();
		scroller.scrollTo(0, state.scroll);
	}

	const dispatch = createEventDispatcher();

	let viewport: HTMLDivElement;
	let scroller: HTMLDivElement;
	let content: HTMLDivElement;

	let offset = 0;
	let top = 0;
	let bottom = 0;
	let heights: number[] = [];

	let lastScrollTop = 0;

	let a = 0;
	//let b = items.length;

	$: b = items.length;
	$: average = heights.reduce((a, b) => a + b, 0) / heights.length;

	function measure(node: HTMLDivElement, id: number) {
		const height = node.clientHeight;
		const current_height = heights[id];

		if (current_height !== height) {
			if (current_height !== undefined) {
				// adjust scroll to account for resized image
				if (node.getBoundingClientRect().top < scroller.getBoundingClientRect().top) {
					scroller.scrollTop += height - current_height;
				}
			}

			heights[id] = height;
		}
	}

	function handle_resize() {
		offset = content.offsetTop;
		handle_scroll(true);
	}

	function handle_scroll(isResizing = false) {
		const scrollTop = scroller.scrollTop;
		const viewportHeight = viewport.clientHeight;

		// Find first visible item
		let i = 0;
		let acc = 0;
		for (; i < b; i += 1) {
			const height = heights[i] ?? average;
			if (acc + height > scrollTop - offset) {
				a = i;
				top = acc;
				break;
			}
			acc += height;
		}

		// Find last visible item (with a lookahead)
		for (; i <= items.length; i += 1) {
			if (acc >= scrollTop + viewportHeight - offset + 200) {
				b = i;
				break;
			}
			acc += heights[i] ?? average;
		}

		// Calculate bottom padding
		bottom = 0;
		for (; i < items.length; i += 1) {
			bottom += heights[i] ?? average;
		}

		// Remember last scroll position
		lastScrollTop = scrollTop;

		// On scrolldown or resize, dispatch 'more' event if below threshold
		if (scrollTop >= lastScrollTop || isResizing) {
			const remaining = scroller.scrollHeight - (scrollTop + viewportHeight);
			if (remaining < FEED_BUTTOM_THRESHOLD_LOADMORE_PX) {
				dispatch('more');
			}
		}
	}

	onMount(handle_resize);
	$: console.log('ITEMS', items);
</script>

<svelte:window on:resize={handle_resize} />

<div bind:this={viewport} class="h-full w-full overflow-hidden">
	<div
		bind:this={scroller}
		class="h-full w-full overflow-y-scroll"
		style="overflow-anchor: none"
		on:scroll={() => handle_scroll(false)}
	>
		<slot name="header" />

		<div bind:this={content} style:padding-top="{top}px" style:padding-bottom="{bottom}px">
			<!-- > TODO: a > 3 ? a - 3 : 0 //  b + 3-->
			{#each (items?.slice(a, b) || []) as item, i (item)}
				<div class="flow-root" data-item-id={a + i} use:measure={a + i}>
					<slot name="item" {item} i={a + i} />
				</div>
			{:else}
				<slot name="empty" />
			{/each}
		</div>

		<slot name="footer" />
	</div>
</div>

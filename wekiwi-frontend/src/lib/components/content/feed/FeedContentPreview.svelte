<script lang="ts">
	import { goto, preloadData, pushState } from '$app/navigation';

	import { enhance } from '$app/forms';

	import { DEFAULT_PLACEHOLDER_AVATAR, MAX_LENGTH_SUBCONTENT } from '$lib/config/constants';

	// Import marked for markdown parsing
	import { marked } from 'marked';

	import { formatDate, truncateText } from '$lib/utils';

	import { RecursiveTreeView, Avatar } from '@skeletonlabs/skeleton';
	import type { TreeViewNode } from '@skeletonlabs/skeleton';

	import SubContentInput from '$lib/components/content/subContent/SubContentInput.svelte';
	import SubContent from '$lib/components/content/subContent/SubContent.svelte';

	// import { getStateContext } from '../../../state';

	import { route } from '$lib/ROUTES';

	import type { PartialContent, PartialContents } from '$lib/directus/directus.types';

	import { ThumbsUp, Share, Share2, Eye } from 'lucide-svelte';
	import { queryParam, ssp } from 'sveltekit-search-params';

	export let content: PartialContent;

	const circles = queryParam('circles');

	let subContents: PartialContents | null = content.child_id ?? null;
	let subContentsNodes: TreeViewNode[] = [];

	if (subContents) {
		subContentsNodes = [
			{
				id: 'root',
				content: '<p>Untergeordnete Inhalte</p>',
				children: transformContentsToNodes(subContents)
			}
		];
	} else {
		subContentsNodes = [
			{
				id: 'root',
				content: '<p>Füge Inhalte hinzu</p>',
				children: [
					{
						id: 'Editor',
						//TODO: optimistically update the UI if content is added
						//@ts-ignore
						content: SubContentInput,
						contentProps: {
							parent_id: content.content_id?.toString()
						}
					}
				]
			}
		];
	}

	function transformContentsToNodes(subContents: PartialContents) {
		//TODO: Use different component to render different types of content?
		let nodes = subContents.map((content) => ({
			id: 'subContent',
			content: SubContent,
			contentProps: {
				subContent: content
			}
		}));
		nodes.push({
			id: 'Editor',
			//TODO: optimistically update the UI if content is added
			//@ts-ignore
			content: SubContentInput,
			//@ts-ignore
			contentProps: {
				//@ts-ignore
				parent_id: content.content_id?.toString()
			}
		});
		return nodes;
	}

	let showFullText = false;
	let contentHeight = 0;
	let containerHeight = 0;

	$: hasOverflow = contentHeight > containerHeight;
</script>

<div class="relative clear-both max-w-[800px] flex-1 p-2">
	<div class="card card-hover overflow-hidden border-4 border-solid border-primary-500 bg-white px-6 py-4 shadow-lg"
	>
		<nav class="mt-2 flex items-center justify-start space-x-4 pb-4 pl-4 pr-4">
			<div class="flex flex-auto items-center justify-between text-sm font-light text-gray-600">
				<!-- this is the profile picture of the user that created the content -->
				<span class="flex items-center space-x-2">
					<Avatar
						width="w-8"
						src={content.user_created?.avatar
							? route('cms_proxy_images', {
									image_id: `${content.user_created?.avatar}`,
									display_config: 'user-preview'
								})
							: DEFAULT_PLACEHOLDER_AVATAR + content?.user_created?.username}
						alt="profile_picture"
					/>

					<!-- this is the name of the user that created the content -->
					<p>{content?.user_created?.username}</p>
				</span>
				<!-- this is the date of content's creation -->
				<p>
					{formatDate(content?.date_created)}
				</p>
				{#if content?.user_updated?.username}
					<Avatar
						width="w-8"
						src={content.user_updated?.avatar
							? route('cms_proxy_images', {
									image_id: `${content.user_created?.avatar}`,
									display_config: 'user-preview'
								})
							: DEFAULT_PLACEHOLDER_AVATAR + content?.user_updated?.username}
						alt="profile_picture"
					/>
					<small>Bearbeitet: {content?.user_updated?.username}</small>
					<small>{formatDate(content?.date_updated)}</small>
				{/if}
			</div>
		</nav>

		<header class="flex flex-col pl-4 pr-4 pt-2">
			<!-- Title of content -->
			<h6 class="h6 font-bold">{content?.title || ''}</h6>

			{#if content.content_type === 'image'}
				<a
					href={route('/app/[content_id=integer]', {
						content_id: content?.content_id?.toString() || ''
					})}
					class="text-primary-900 hover:text-primary-500"
					target="_blank"
				>
					<img
						src={content.content_url}
						class="aspect-[21/9] w-full bg-black/50"
						alt={content.title}
					/>
				</a>
			{/if}
		</header>

		<div class="space-y-4 p-4">
			{#if content.content_type === 'text'}
				<article class="prose relative">
					{#if content.text}
						<!-- Content text -->
						{#if showFullText}
							<div class="content-expanded">
								{@html content?.text ? marked(content.text) : ''}
							</div>
						{:else}
							<div class="preview-container" bind:clientHeight={containerHeight}>
								<div class="preview-content" bind:clientHeight={contentHeight}>
									{@html content?.text ? marked(content.text) : ''}
								</div>
							</div>
						{/if}

						{#if hasOverflow}
							<div class="sticky-button bg-white border-t border-gray-100 pt-2 mt-2">
								<div class="flex items-center gap-2">
									{#if !showFullText}
										<span class="text-xs">...</span>
									{/if}
									<button
										class="text-xs"
										on:click={(e) => {
											e.stopPropagation();
											showFullText = !showFullText;
										}}
									>
										{showFullText ? 'Weniger anzeigen' : 'Mehr anzeigen'}
									</button>
								</div>
							</div>
						{/if}
					{:else}
						<p>Kein Text vorhanden</p>
					{/if}
				</article>
			{:else}
				<div class="flex flex-col space-y-2">
					<h3 class="h3">{content.title}</h3>
				</div>
			{/if}
		</div>

		<footer class="mt-2 flex items-center justify-end pb-4 pl-4 pr-4">
			<div class="">
				<a
					href={route('/app/[content_id=integer]', {
						content_id: content?.content_id?.toString() || '',
						circles: $circles || ''
					})}
					class="variant-soft chip w-20 bg-primary-500 py-2 hover:variant-filled"
					target="_blank"
					on:click={async (e) => {
						if (e.metaKey) return; // user wants to open in a new tab

						e.preventDefault(); // prevent the default link behavior

						const { href } = e.currentTarget;

						// we could just use the item from the existing data but
						// a) it might be stale and b) we might want to load/show additional data
						const result = await preloadData(href);

						if (result.type === 'loaded' && result.status === 200) {
							result.data.circleUsers = []; //await result.data.circleUsers;
							pushState(href, { contentSelect: result.data });
						} else {
							// error navigate to the page
							goto(href);
						}
					}}
				>
					<Eye size={22} color="#ffffff" strokeWidth={1.5} />
				</a>
			</div>
			<!-- <div class="flex items-center"> -->
			<!-- contentReaction -->
			<div class="flex justify-center space-x-2">
				<form
					method="POST"
					action={route('contentReaction /app/[content_id=integer]', {
						// @ts-ignore
						content_id: content.content_id.toString(),
						reaction_type: 'like'
					})}
					use:enhance={() => {
						return async ({ result }) => {
							if (result.type === 'failure' || result.type === 'error') {
								//remove like on failure or error
							}
						};
					}}
				>
					<!-- <button class="variant-soft chip py-2 text-xs hover:variant-filled">
							<ThumbsUp size={20} color="#ffffff" strokeWidth={1.5} />
							<span class="screen-reader-only">Like</span>
						</button> -->
				</form>

				<!-- shareContent -->
				<!-- TODO: This should open a modal not be a formaction! -->
				<!-- <form
						method="POST"
						action={route('shareContent /app/[content_id=integer]', {
							// @ts-ignore
							content_id: content.content_id.toString(),
							circles: $page.params.circle_name
						})}
						use:enhance
					>
						<button class="variant-soft chip py-2 hover:variant-filled">
							<Share2 size={20} color="#ffffff" strokeWidth={1.5} />
							<span class="screen-reader-only">Share</span>
						</button>
					</form>
				</div> -->
				<!-- </div> -->
			</div>
		</footer>

		<!-- {#if subContents}
			<div class="bg-primary-100-800-token">
				<RecursiveTreeView
					class="bg-surface-50-900-token"
					padding="p-3"
					expandedNodes={expanded ? ['root'] : []}
					on:toggle={() => {
						dispatch('expand', {
							//https://www.skeleton.dev/components/tree-views?tab=properties
							content_id: subContent?.content_id?.toString()
						});
					}}
					nodes={subContentsNodes}
				/>
			</div>
		{/if} -->
	</div>
</div>

<style>
	.preview-container {
		position: relative;
		height: 8em; /* Fixed height instead of max-height */
		overflow: hidden;
	}
	
	.preview-content {
		position: absolute; /* Take out of flow to get real height */
		width: 100%;
		padding-bottom: 2em;
	}
	
	.preview-container::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 2em;
		background: linear-gradient(transparent, white);
		pointer-events: none;
	}
	
	.content-expanded {
		max-height: 500px;
		overflow-y: auto;
		padding-bottom: 40px; /* Make room for sticky button */
	}
	
	.sticky-button {
		position: sticky;
		bottom: 0;
		z-index: 10;
	}
</style>

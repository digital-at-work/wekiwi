<script>
	import '../app.pcss';

	import { navigating } from '$app/stores';
	import PreloadingIndicator from '$lib/components/ui/PreloadingIndicator.svelte';

	import { page } from '$app/stores';

	import { queryParameters, ssp } from 'sveltekit-search-params';

	import Modal from '$lib/components/ui/Modal.svelte';
	import ContentCreate from './app/(content)/content_create/+page.svelte';

	import TopNav from '$lib/components/ui/nav/TopNav.svelte';
	import FooterNav from '$lib/components/ui/nav/FooterNav.svelte';

	import { setDirectusClient } from '$lib/directus/directus';
	import { setDirectusClientProxy } from '$lib/directus/directus';
	import { setStateContext } from '$lib/state';

	import { initializeStores } from '@skeletonlabs/skeleton';
	import { Toast, getToastStore, getModalStore } from '@skeletonlabs/skeleton';

	import { getFlash } from 'sveltekit-flash-message';

	import ContentPage from './app/(content)/[content_id=integer]/+page.svelte';

	import ShareContent from '$lib/components/ui/ShareContent.svelte';

	export let data;

	// Not working for now. Proxy has to be used instead
	setDirectusClient('session', fetch);
	setDirectusClientProxy(fetch);

	// Set the context for the state store that caches content on the client
	setStateContext();

	initializeStores();
	const modalStore = getModalStore();
	const toastStore = getToastStore();

	const flash = getFlash(page);
	const flashTypeToColor = {
		success: 'variant-filled-primary',
		error: 'variant-filled-error',
		warning: 'variant-filled-warning',
		info: 'variant-filled-secondary'
	};

	$: if ($flash) {
		toastStore.trigger({
			message: $flash.message,
			background: flashTypeToColor[$flash.type],
			timeout: $flash.timeout || 2800
		});

		// Clear the flash message to avoid double-toasting.
		$flash = undefined;
	}

	const params = queryParameters({
		search: ssp.string(),
		ai: ssp.boolean()
	});

	let contentTitle = $params.search || '';
</script>

<Toast />

{#if $navigating}
	<PreloadingIndicator />
{/if}

<!-- Create Content (Shallow routing) -->
{#if $page.state.contentCreate}
	<Modal on:close={() => history.back()} location="justify-end" blur={true}>
		<div class="height-screen max-h-[188rem] w-screen max-w-4xl p-8">
			<div class="flex flex-col rounded-md border-4 border-primary-500 bg-white p-2 shadow-xl">
				<ContentCreate bind:contentTitle data={$page.state.contentCreate} />
			</div>
		</div>
	</Modal>
{/if}

<!-- Content Page (Shallow routing) -->
{#if $page.state.contentSelect}
	<Modal on:close={() => history.back()} blur={true}>
		<div class="height-screen max-h-[188rem] w-screen max-w-5xl p-8">
			<div class="flex flex-col rounded-md bg-white p-2 shadow-xl">
				<ContentPage data={$page.state.contentSelect} />
			</div>
		</div>
	</Modal>
{/if}

<!-- Share Content Modal -->
{#if $modalStore[0]?.meta?.type === 'share'}
	<Modal on:close={() => modalStore.clear()} blur={false}>
		<div class="height-screen max-h-[188rem] w-screen max-w-5xl p-8">
			<div class="flex flex-col rounded-md bg-white p-2 shadow-xl">
				<ShareContent
					content_id={$modalStore[0].meta?.content_id}
					shareContentForm={data.contentShareForm}
				/>
			</div>
		</div>
	</Modal>
{/if}

<div class="h-screen grid grid-rows-[auto_1fr_auto]">
	<!-- Header -->
	<header class="sticky top-0 w-full">
		<TopNav bind:contentTitle {params} />
	</header>

	      <!-- Main Area -->
		  <main class="h-full">
			<slot /> 
		  </main>

	<!-- Footer -->
	<footer class="sticky bottom-0 w-full">
		<FooterNav />
	</footer>
</div>

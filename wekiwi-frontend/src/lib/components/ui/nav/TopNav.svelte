<script lang="ts">
	import { page } from '$app/stores';
	import { invalidate } from '$app/navigation';
	import { enhance } from '$app/forms';
	import { goto, preloadData, pushState } from '$app/navigation';

	import { route } from '$lib/ROUTES';

	import { AppBar } from '@skeletonlabs/skeleton';

	import AnimatedLogo from '../AnimatedLogo.svelte';
	import { Home, Search, X, LogOut } from 'lucide-svelte';

	import { afterNavigate } from '$app/navigation';

	export let contentTitle = '';
	export let params;

	let shouldRefocus = false;
	let searchElement: HTMLInputElement;

	function clearSearch() {
		$params.search = '';
		contentTitle = '';
	}

	function submitSearch() {
		if (contentTitle !== '') {
			shouldRefocus = document.activeElement === searchElement;  // Check if input is focused
			
			const newUrl = new URL($page.url);
			newUrl.searchParams?.set('c_id', $page.data.user?.company_id);
			newUrl.searchParams?.set('search', contentTitle);
			goto(newUrl, { invalidate: ['data:feed'] });
		}
	}

	afterNavigate(() => {
		if (shouldRefocus) {
			searchElement.focus();  // Restore focus to the search input
			shouldRefocus = false;  // Reset the flag
		}
	});


	function onWindowKeydown(e: KeyboardEvent): void {
		if ((e.metaKey || e.ctrlKey) && e.key === 'd') {
			e.preventDefault();
			searchElement.focus();  // Focus on search element on shortcut
		}

		if (document.activeElement === searchElement) {
			if (e.key === 'Escape' || (e.key === 'Backspace' && contentTitle.length === 1)) {
			clearSearch();
			}

			if (e.key === 'Enter') {
			e.preventDefault();  // Prevent default form submission
			submitSearch();  // Trigger search
			}
		}
	}

</script>

<svelte:window on:keydown|stopPropagation={onWindowKeydown} />

<AppBar
	background="bg-surface-50-900-token"
	border="border-b-2 border-primary-400-500-token"
	padding="p-4"
	gridColumns="grid-cols-[3fr_16fr_3fr]"
	slotLead=""
	slotDefault="col-start-2 grid gap-2 grid-cols-[1fr_10fr_2fr] md:gap-4"
	slotTrail="flex justify-end"
>
	<svelte:fragment slot="lead">
		<a href={route('/')}>
			<AnimatedLogo />
		</a>
	</svelte:fragment>

	<svelte:fragment slot="default">
		{#if $page.url.pathname === '/app/feed'}
			<!-- Search Bar -->
			<div
				class="col-start-2 grid border-2 input-group input-group-divider grid-cols-[auto_1fr_auto]"
			>
				<div class="input-group-shim">
					<Search size="1.5em" />
				</div>
				<input
					name="search"
					type="text"
					bind:value={contentTitle}
					bind:this={searchElement}
					placeholder="Worum geht's?"
				/>
				{#if contentTitle !== ''}
					<button
						on:click={clearSearch}
						class="input-group-shim font-medium text-surface-500"
						>Leeren
					</button>
				{/if}
			</div>

			<div class="col-start-3 flex gap-4">
				<label class="flex items-center space-x-2 text-sm md:whitespace-nowrap md:text-base">
					<input name="ki-suche" class="checkbox" type="checkbox" bind:checked={$params.ai} />
					<span>KI Suche</span>
				</label>
				<button on:click={submitSearch} class="variant-filled-primary btn btn-sm">Search</button>
				<a
					href={route('/app/content_create', {
						circles: $params.circles || '[]',
						c_id: $page.data.user?.company_id
					})}
					data-sveltekit-preload-code="eager"
					on:click={async (e) => {
						if (e.metaKey) return; // user wants to open in a new tab
						e.preventDefault(); // prevent the default link behavior
						const { href } = e.currentTarget;
						// we could just use the item from the existing data but
						// a) it might be stale and b) we might want to show additional data
						const result = await preloadData(href);
						if (result.type === 'loaded' && result.status === 200) {
							result.data.circleUsers = await result.data.circleUsers;
							pushState('', { contentCreate: result.data });
						} else {
							// some error happened! try navigating to the page
							goto(href);
						}
					}}
					class="variant-filled-primary btn btn-sm md:btn"
				>
					Make Post
				</a>
			</div>
		{/if}
	</svelte:fragment>

	<svelte:fragment slot="trail">
		<a
			class="btn btn-sm hidden border border-primary-500 md:inline-flex {$page.url.pathname ===
			route('/')
				? 'variant-ringed-primary text-primary-500'
				: 'variant-filled-primary'}"
			href={route('/')}
		>
			Home
		</a>
		{#if $page.url.pathname !== route('/')}
			<a
				class="btn btn-sm border-2 border-primary-500 md:hidden variant-filled-primary}"
				href={route('/')}
			>
				<Home class="h-4 w-4" />
			</a>
		{/if}

		{#if $page.data.user?.id}
			<!-- Profil Button -->
			<!-- Profil Button commented out for now 
			<a
				class="btn btn-sm {$page.url.pathname === route('/profile') ? 'variant-ghost-surface' : 'variant-filled-primary'}"
				href={route('/profile')}
			>
				Profil
			</a> -->

			<!-- Log out Button -->
			<form method="POST" action={route('default /auth/sign-out')} use:enhance>
				<!-- TODO: display <LogOut size="1.5em" /> instead on small screens -->
				<button class="btn btn-sm hidden border-2 border-error-500 text-error-500 md:inline-flex">
					Abmelden
				</button>
				<button class="btn btn-sm border-2 border-error-500 text-error-500 md:hidden">
					<LogOut class="h-4 w-4" />
				</button>
			</form>
			<!-- Display if user is not logged in -->
		{:else if $page.url.pathname !== route('/auth/sign-up') && $page.url.pathname !== route('/auth/sign-in')}
		<!-- Register Button -->
			<a class="btn btn-sm variant-filled-primary" href={route('/auth/sign-up')}> Registrieren </a>
			
			<!-- Login Button -->
			 <a class="btn btn-sm variant-filled-primary" href={route('/auth/sign-in')}> Anmelden </a>
		{/if}
	</svelte:fragment>
</AppBar>

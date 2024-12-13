<script lang="ts">
	import { page } from '$app/stores';

	import { queryParameters, ssp } from 'sveltekit-search-params';

	import { AppRail, AppRailTile } from '@skeletonlabs/skeleton';

	import type { PartialUser } from '$lib/directus/directus.types';

	import { Text, Image, FileText } from 'lucide-svelte';

	export let usersCircles: { id: string; name: string }[] = [];
	export let circleUsers: Promise<PartialUser[]>;

	const params = queryParameters({
		// ai: ssp.boolean(),
		circles: ssp.array(),
		sort1: {
			encode: (array: string[]) => array.join(''),
			decode: (stringValue) => stringValue?.match(/(-)?(.+)/)?.slice(1) || ['', '']
		},
		sort2: {
			encode: (array: string[]) => array.join(''),
			decode: (stringValue) => stringValue?.match(/(-)?(.+)/)?.slice(1) || ['', '']
		}
	});

	const sortFieldOptions = [
		{ value: '', label: '-' },
		{ value: 'date_created', label: 'Date Created' },
		{ value: 'date_updated', label: 'Date Updated' },
		{ value: 'user_created', label: 'Created By' },
		{ value: 'user_updated', label: 'Updated By' },
		{ value: 'title', label: 'Title' }
	];

	const sortOrderOptions = [
		{ value: '', label: 'Ascending' },
		{ value: '-', label: 'Descending' }
	];

	const dateOptions = [
		{ value: '', label: '-' },
		{ value: '_between', label: 'Is Between' },
		{ value: '_lt', label: 'Is Before' },
		{ value: '_gt', label: 'Is After' },
		{ value: '_eq', label: 'Is Equal To' },
		{ value: '_neq', label: 'Is Not Equal To' },
		{ value: '_lte', label: 'Is Before or Equal To' },
		{ value: '_gte', label: 'Is After or Equal To' }
	];

	const typeOptions = [
		{ name: 'text', value: 'text', component: Text },
		{ name: 'image', value: 'image', component: Image },
		{ name: 'document', value: 'document', component: FileText }
	];
</script>

<div>
	<AppRail class="bg-surface-200-600-token mx-2 h-full w-full rounded-lg shadow-2xl">
		<svelte:fragment slot="lead">
			<h2 class="pl-2 pt-2 text-2xl font-bold">Filters</h2>
		</svelte:fragment>

		<!-- Type Filter -->
		<!-- <div class="flex justify-center">
			<div class="flex w-12 justify-evenly">
				{#each typeOptions as option}
					<AppRailTile
						bind:group={$params.type}
						class="h-12"
						name={option.name}
						value={option.value}
					>
						<div class="flex w-12 justify-center">
							<svelte:component this={option.component} />
						</div>
					</AppRailTile>
				{/each}
			</div>
		</div> -->

		<!-- User Created Filter -->
		<div class="my-4">
			<span class="mx-2 mt-4 font-semibold">Created By</span>
			<select
				name="createdBy"
				class="select m-2 w-11/12 rounded-md"
				bind:value={$params.usercreated}
			>
				<option value="">-</option>
				{#await circleUsers}
					Loading...
				{:then circleUsers}
					{#each [$page.data.user, ...circleUsers] as user}
						<option
							class="m-2"
							value={user.username}
							selected={user.username === $params.usercreated}
							>{`${user.first_name} ${user.last_name}`}</option
						>
						{user.username}
					{/each}
				{:catch error}
					<option class="text-red-500" disabled>{error.message}</option>
				{/await}
			</select>
		</div>

		<!-- User Updated Filter -->
		<!-- <div class="my-4">
			<label for="updatedBy" class="mx-2 mt-4 font-semibold">Updated By</label>
			<select name="updatedBy" class="select m-2 w-11/12 rounded-md" bind:value={$params.userupdated}>
				<option value="">-</option>
				{#await circleUsers}
					Loading...
				{:then users}
					{#each users as user}
						<option
							class="m-2"
							value={user.username}
							selected={user.username === $params.userupdated}
							>{`${user.username} - ${user.first_name} ${user.last_name}`}</option
						>
					{/each}
				{:catch error}
					<option class="text-red-500" disabled>{error.message}</option>
				{/await}
			</select>
		</div> -->

		<!-- Date Created Filter -->
		<div class="mx-2 my-4 space-y-2">
			<span class="mt-4 font-semibold">Created Date</span>
			<select name="datelogic1" class="select w-11/12 rounded-md" bind:value={$params.datelogic1}>
				{#each dateOptions as option}
					<option selected={option.value === $params.datelogic1} value={option.value}
						>{option.label}</option
					>
				{/each}Schreiben
			</select>
			<input type="date" bind:value={$params.datecreated1} class="input w-11/12 rounded-md" />
			<input type="date" bind:value={$params.datecreated2} class="input w-11/12 rounded-md" />
		</div>

		<!-- Date Updated Filter -->
		<!-- <div class="my-4">
			<label for="datelogic2" class="m-2 mt-2 font-semibold">Updated Date</label>
			<select name="datelogic2" class="select m-2 w-11/12 rounded-md" disabled={$params.ai} bind:value={$params.datelogic2}>
				{#each dateOptions as option}
					<option selected={option.value === $params.datelogic2} value={option.value}
						>{option.label}</option
					>
				{/each}
			</select>
			<input
				bind:value={$params.dateupdated1}
				class="input m-2 h-9 w-11/12 rounded-md"
			/>
			<input type="date" bind:value={$params.dateupdated2} class="input m-2 w-11/12 rounded-md" />
		</div> -->

		<!-- First Sort -->
		<!-- <div class="my-4">
			<label for="sort1" class="m-2 mt-2 font-semibold">Sort 1</label>
			<select name="sort1" class="select m-2 w-11/12 rounded-md" disabled={$params.ai} bind:value={$params.sort1[1]}>
				{#each sortFieldOptions as option}
					<option selected={option.value === $params.sort1[1]} value={option.value}
						>{option.label}</option
					>
				{/each}
			</select>
			<select class="select m-2 w-11/12 rounded-md" disabled={$params.ai} bind:value={$params.sort1[0]}>
				{#each sortOrderOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		</div> -->

		<!-- Second Sort -->
		<!-- <div class="my-4">
			<label for="sort2" class="m-2 mt-2 font-semibold">Sort 2</label>
			<select name="sort2" class="select m-2 w-11/12 rounded-md" disabled={$params.ai} bind:value={$params.sort2[1]}>
				{#each sortFieldOptions as option}
					<option selected={option.value === $params.sort2[1]} value={option.value}
						>{option.label}</option
					>
				{/each}
			</select>
			<select class="select m-2 w-11/12 rounded-md" disabled={$params.ai} bind:value={$params.sort2[0]}>
				{#each sortOrderOptions as option}
					<option value={option.value}>{option.label}</option>
				{/each}
			</select>
		</div> -->

		<!-- Circles Filter -->
		<div class="mx-2 my-2">
			<span class="font-semibold">Circles</span>
			<div class="h-22 overflow-auto">
				{#each usersCircles as circle}
					<label class="flex items-center space-x-2">
						<input
							class="checkbox"
							type="checkbox"
							bind:group={$params.circles}
							value={circle.id}
							name="circles"
						/>
						<p>{circle.name}</p>
					</label>
				{/each}
			</div>
		</div>

		<!-- Reset Filters -->
		<div class="p-4">
			<button
				class="align-center variant-filled-secondary chip"
				on:click={() =>
					params.update((currentObject) => {
						for (let key in currentObject) {
							switch (key) {
								case 'type':
									break;
								case 'circles':
									currentObject[key] = usersCircles.map((obj) => Number(obj.id));
									break;
								case 'sort1':
								case 'sort2':
									currentObject[key] = ['', ''];
									break;
								case 'c_id':
								case 'ai':
									break;
								default:
									currentObject[key] = null;
							}
						}
						return currentObject;
					})}
			>
				Reset Filters
			</button>
		</div>
	</AppRail>
</div>

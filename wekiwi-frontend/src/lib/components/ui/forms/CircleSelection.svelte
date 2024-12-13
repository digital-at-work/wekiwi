<script lang="ts">
	import { page } from '$app/stores';

	import { arrayProxy } from 'sveltekit-superforms';

	export let superform;
	export let field;

	const { errors, values, valueErrors } = arrayProxy(superform, field);
</script>

<div>
	<span class="font-semibold">Circles</span>
	<div class="h-22 overflow-auto">
		{#each $page.data.user.circles ?? [] as circle}
			<label class="flex items-center space-x-2">
				<input
					type="checkbox"
					name="circles"
					class="checkbox"
					data-invalid={$errors}
					value={circle.id}
					bind:group={$values}
				/>
				<p>{circle.name}</p>
			</label>
		{/each}
	</div>
	{#if $valueErrors}
		<span class="text-error-500">{$valueErrors}</span>
	{/if}
</div>

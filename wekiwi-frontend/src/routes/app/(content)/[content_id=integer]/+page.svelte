<script lang="ts">
	import Content from '$lib/components/content/Content.svelte';
	import SubContent from '$lib/components/content/subContent/SubContent.svelte';
	import SubContentInput from '$lib/components/content/subContent/SubContentInput.svelte';

	import { ssp, queryParameters } from 'sveltekit-search-params';

	export let data;

	const params = queryParameters({
		circles: ssp.array(data.content?.circle_contents?.map((c) => c.circle_id) as number[] || []),
	});
</script>

<svelte:head>
	<title>Wekiwi - {data?.content?.title}</title>
</svelte:head>

<div class="page-container-wide page-padding">
	<div>
		<div class="flex flex-col">
			<Content
				content={data.content ?? {}}
				content_circles={$params.circles}
				circleUsers={data.circleUsers}
				contentEditForm={data.contentEditForm}
				on:contentChange={(e) => {
					data.content = { ...data.content, ...e.detail };
				}}
			/>
		</div>
	</div>

	<h3 class="h3">
		Diskussion
		<hr />
	</h3>

	<div class="flex flex-col">
		{#if !!data.content?.child_id?.length}
			{#each data.content.child_id as subContent (subContent.content_id)}
				{#if !subContent?.file_id}
					<SubContent
						subContent={subContent ?? {}}
						circleUsers={data.circleUsers}
						parent_circles={$params.circles}
						subContentEditForm={data.contentEditForm}
						on:deleteContent={(e) => {
							if (!data.content?.child_id) return;
							data.content.child_id = data.content?.child_id.filter(
								(c) => c.content_id !== e.detail.content_id
							);
						}}
					/>
				{/if}
			{/each}
		{:else}
			<div class="flex flex-col items-center">
				<div class="text-lg">Noch keine Beiträge vorhanden. Hast du etwas beizutragen?</div>
			</div>
		{/if}
		<SubContentInput
			parent_id={data.content?.content_id.toString()}
			parent_circles={$params.circles}
			contentCreateForm={data.contentCreateForm}
			circleUsers={data.circleUsers}
			on:subContentInput={(e) => {
				if (data.content?.child_id) {
					data.content.child_id = [...data.content.child_id, { ...e.detail }];
				}
			}}
		/>
	</div>
</div>

<script lang="ts">
	import ContentInput from '$lib/components/content/ContentInput.svelte';

	export let data;
	export let contentTitle: string;
</script>

<!-- Shallow routing in modal, see: https://kit.svelte.dev/docs/shallow-routing -->
<div class="page-container-wide page-padding">
	<ContentInput
		circleUsers={data.circleUsers}
		contentCreateForm={data.contentCreateForm}
		bind:contentTitle
	/>
</div>

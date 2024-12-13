<script lang="ts">
	import { page } from '$app/stores';
	import { AppBar } from '@skeletonlabs/skeleton';
</script>


{#if ['/','/app','/sign-in','/sign-up'].includes($page.url.pathname)}
	<AppBar
		border="border-t-2 border-primary-500"
		background="bg-white dark:bg-surface-50-900-token"
		regionRowMain="h-12"
	>
	</AppBar>
{/if}
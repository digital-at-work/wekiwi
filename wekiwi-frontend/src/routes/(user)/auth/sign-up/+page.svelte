<script lang="ts">
    import { TabGroup, Tab } from '@skeletonlabs/skeleton';
    import { page } from '$app/stores';

    import { Users, UserRoundPlus } from 'lucide-svelte';

    import SignIn from '$lib/components/auth/sign-in.svelte';
    import SignUp from '$lib/components/auth/sign-up.svelte';

    export let data;

    let tab = $page.url.pathname.split('/').pop();
    let tabSet: string = tab === 'sign-up' ? 'signUp' : 'signIn';
</script>

<svelte:head>
	<title>Registierung • WeKiwi</title>
</svelte:head>

<div class="flex flex-row justify-center items-center mb-4">
    <div>
        {#if tabSet === 'signIn'}
            <Users />
        {:else if tabSet === 'signUp'}
            <UserRoundPlus />
        {/if}
    </div>
</div>

<TabGroup justify="justify-center">
    <Tab bind:group={tabSet} name="signInTab" value={'signIn'}>Anmelden</Tab>
    <Tab bind:group={tabSet} name="signUpTab" value={'signUp'}>Registrieren</Tab>
    <!-- Tab Panels -->
    <svelte:fragment slot="panel">
        {#if tabSet === 'signIn'}
            <SignIn {data} />
        {:else if tabSet === 'signUp'}
            <SignUp {data} />
        {/if}
    </svelte:fragment>
</TabGroup>

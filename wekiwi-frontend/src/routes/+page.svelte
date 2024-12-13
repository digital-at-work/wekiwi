<script lang="ts">
	import type { PageData } from './$types';
	import Typewriter from '$lib/components/ui/typewriter/Typewriter.svelte';
	import { typewriterSentences } from '$lib/components/ui/typewriter/typewriterSentences';
	import { route } from '$lib/ROUTES';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	export let data: PageData;
	console.log("data object here", data);

	const userFirstName = data.user?.first_name;
	const userLastName = data.user?.last_name;
	const userEmail = data.user?.email;

	let formData = {
		vorname: userFirstName,
		nachname: userLastName,
		email: userEmail,
		formCircleName: '',
		message: '',
		email_list: ''
	};

	let emails: string[] = [];
	let emailInput: string = '';
	let emailError: string = '';
	let paidCircle: string = '';
	let showModal = false;

	async function handleSubmit(event) {
		event.preventDefault();
		formData.email_list = emails.join(', ');
		try {
			const response = await fetch(
				'https://cms.wekiwi.de/flows/trigger/40e9aff1-c45e-492e-a8c8-1eafc9f42c90',
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						Accept: 'application/json'
					},
					body: JSON.stringify(formData)
				}
			);
			if (response.ok) {
				showModal = true;
			} else {
				console.error('Failed to send form data');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}

	function addEmail() {
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (!emailRegex.test(emailInput)) {
			emailError = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.';
		} else if (emails.includes(emailInput)) {
			emailError = 'Diese E-Mail-Adresse wurde bereits hinzugefügt.';
		} else {
			emails = [...emails, emailInput];
			emailInput = '';
			emailError = '';
		}
	}

	function removeEmail(email: string) {
		emails = emails.filter((e) => e !== email);
	}

	function closeModal() {
		showModal = false;
		window.location.href = 'https://news.wekiwi.de/';
	}

	function checkCircleSize() {
		if (emails.length > 4) {
			paidCircle = 'Achtung: circles mehr als funf users sind kostenpflichtig';
		} else {
			paidCircle = '';
		}
	}
</script>

<section class="flex h-24 flex-col items-center justify-center bg-primary-500 text-white md:h-64">
	<div class="p-2 text-4xl md:text-7xl">we:kiwi</div>
	<div class="text-2xl md:text-4xl">Ein Ort für Dein Wissen.</div>
</section>

<div class="flex flex-col items-center justify-center p-8 md:text-4xl">
	{#if !data.user}
		<Typewriter sentences={typewriterSentences} />
	{:else}
		<ul class="list">
			{#each data.circles ?? [] as circle}
				<li class="list-none border-2 p-2 text-center">
					<span class="flex-auto">
						<a
							data-sveltekit-preload-code="eager"
							href={route('/app/feed', {
								circles: `[${circle?.circle_id}]`,
								c_id: $page.data.user?.company_id
							})}
						>
							{circle?.circle_name}
						</a>
					</span>
				</li>
			{/each}
			{#if data.circles}
				<li class="list-none border-2 p-2 text-center">
					<span class="flex-auto">
						<a
							data-sveltekit-preload-data
							href={route('/app/feed', {
								circles: `[${data.circles?.map((obj) => obj.circle_id)}]`,
								c_id: $page.data.user?.company_id
							})}
						>
							Alle Circles anzeigen
						</a>
					</span>
				</li>
			{:else}
				<div class="w-full max-w-md rounded-lg bg-white p-8 text-center shadow-lg">
					<h1 class="mb-4 text-2xl font-bold">
						Hallo {`${userFirstName} ${userLastName}`} Willkommen bei we:kiwi!
					</h1>
					<h6 class="mb-6 text-xl font-medium text-gray-700">
						Du bist noch keinem Circle beigetreten. Fülle das folgende Formular aus, um einen Circle
						für dich und dein Team zu bekommen.
					</h6>
					<form class="space-y-4" on:submit|preventDefault={handleSubmit}>
						<div>
							<input
								class="focus:ring-primary-color input w-full rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2"
								title="Input (text)"
								type="hidden"
								placeholder="Vorname"
								bind:value={formData.vorname}
								required
							/>
						</div>
						<div>
							<input
								class="focus:ring-primary-color input w-full rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2"
								title="Input (text)"
								type="hidden"
								placeholder="Nachname"
								bind:value={formData.nachname}
								required
							/>
						</div>
						<div>
							<input
								class="focus:ring-primary-color input w-full rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2"
								title="Input (text)"
								type="hidden"
								placeholder="Email"
								bind:value={formData.email}
								required
							/>
						</div>
						<div>
							<input
								class="focus:ring-primary-color input w-full rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2"
								title="Input (text)"
								type="text"
								placeholder="Circle-Namen wählen"
								bind:value={formData.formCircleName}
								required
							/>
						</div>
						<div>
							<textarea
								class="focus:ring-primary-color textarea w-full rounded-md border border-gray-300 px-4 py-2 focus:outline-none focus:ring-2"
								rows="4"
								placeholder="Beschreibe, was du brauchst"
								bind:value={formData.message}
								required
							></textarea>
						</div>

						<div>
							<div class="flex flex-col items-center">
								<input
									class="focus:ring-primary-color input w-full max-w-md rounded-md border border-gray-300 px-4 py-2 text-sm focus:outline-none focus:ring-2"
									placeholder="E-mail-Adressen weiterer Mitglieder"
									bind:value={emailInput}
									on:keydown={(e) => e.key === 'Enter' && addEmail()}
								/>
								{#if emailError}
									<p class="mt-2 text-sm text-red-500">{emailError}</p>
								{/if}
								
								<button
									type="button"
									on:click={addEmail}
									on:click={checkCircleSize}
									class="hover:bg-warning-dark bg-warning-color variant-filled-warning btn mt-2 w-full max-w-md rounded-md py-2 text-sm text-white"
								>
									E-Mail hinzufügen
								</button>
							</div>

							{#if emails.length > 0}
								<ul
									class="scrollable-email-list mx-auto mt-4 max-w-md space-y-2 rounded-md border border-gray-300 p-4 text-sm"
								>
									{#each emails as email, index}
										<li class="flex justify-between border-b py-2">
											<span class="truncate">{email}</span>
											<button
												type="button"
												on:click={() => removeEmail(email)}
												class="text-sm text-red-500"
											>
												Entfernen
											</button>
										</li>
									{/each}
								</ul>
								{#if paidCircle}
									<p class="mt-2 text-sm text-red-500">{paidCircle}</p>
								{/if}
							{/if}
						</div>
						<div class="mb-5">
							<button
								type="submit"
								class="hover:bg-primary-dark bg-primary-color variant-filled-primary btn w-full rounded-md py-2 text-white"
							>
								<p>Senden</p>
							</button>
						</div>
					</form>
				</div>

				{#if showModal}
					<div class="modal-overlay">
						<div class="modal-content">
							<div class="fixed inset-0 flex items-center justify-center bg-gray-500 bg-opacity-75">
								<div class="rounded-lg bg-white p-6 shadow-lg">
									<h2 class="mb-4 text-xl font-bold">Formular eingereicht</h2>
									<p class="mb-4">
										Deine Informationen werden manuell verarbeitet und du erhältst eine E-Mail, wenn
										dies abgeschlossen ist.
									</p>
									<button on:click={closeModal} class="btn-blue btn">Alles Klar</button>
								</div>
							</div>
						</div>
					</div>
				{/if}
			{/if}
		</ul>
	{/if}
</div>

<div class="fixed bottom-24 right-2 m-4 flex w-[12%] min-w-40 flex-col gap-2">
	<a
		class="variant-filled-primary btn btn-sm"
		href="https://www.news.wekiwi.de"
		target="_blank"
		rel="noopener noreferrer">Mehr über we:kiwi</a
	>
	<a
		class="variant-filled-primary btn btn-sm"
		href="https://news.wekiwi.de/kontakt/"
		target="_blank"
		rel="noopener noreferrer">Kontakt</a
	>
</div>

<style>
	.modal-overlay {
		position: fixed;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		background: rgba(0, 0, 0, 0.5);
	}

	.modal-content {
		background: white;
		padding: 1.5rem;
		border-radius: 0.5rem;
		width: 50%;
		max-width: 200px;
		text-align: center;
		box-shadow: 0px 10px 20px rgba(0, 0, 0, 0.1);
	}

	.modal-content button {
		margin-top: 1rem;
	}

	.btn {
		@apply rounded px-4 py-2 font-bold;
	}
	.btn-blue {
		@apply bg-blue-500 text-white;
	}
	.btn-blue:hover {
		@apply bg-blue-700;
	}

	.truncate {
		max-width: 70%;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.scrollable-email-list {
		max-height: 80px; 
		overflow-y: scroll; 
	}

	.scrollable-email-list::-webkit-scrollbar {
		width: 8px;
	}

	.scrollable-email-list::-webkit-scrollbar-thumb {
		background-color: rgba(0, 0, 0, 0.3);
		border-radius: 4px;
	}

	.scrollable-email-list::-webkit-scrollbar-track {
		background-color: rgba(0, 0, 0, 0.1);
	}
</style>

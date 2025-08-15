<script lang="ts">
	import { createEventDispatcher, onDestroy, onMount } from 'svelte';

	import { base } from '$app/paths';
	import type { PartialUser } from '$lib/directus/directus.types';
	import { getDirectusClientProxy } from '$lib/directus/directus';

	import { route } from '$lib/ROUTES';

	import Editor from '@tinymce/tinymce-svelte';

	import { uploadFiles } from '@directus/sdk';

	export let textContent: string = '';
	export let htmlContent: string = '';
	export let inline: boolean = false;
	export let readonly: boolean = true;
	export let circleUsers: PartialUser[];
	export let mentions: { id: number; username: string }[] = [];
	export let height: number = 400;
	export let minHeight: number = 200;
	export let minWidth: number = 150;
	export let cssClasses: string = 'tinymce-wrapper';
	export let placeholder: string = `Nutze Formatierungsoptionen, um Deinen Beitrag zu gestalten.`;
	export let editorMenuBar: string = 'edit view insert format tools help';
	export let editorToolBar: string =
		'chatPlugin | audioPlugin | undo redo | bold italic underline | align numlist bullist checklist | link emoticons codesample | strikethrough blocks fontfamily fontsize | lineheight | forecolor backcolor removeformat | fullscreen | print | anchor accordion accordionremove';

	const directusClient = getDirectusClientProxy();

	// API key is now handled server-side in the proxy

	async function imageUploadHandler(blobInfo: any, progress: any) {
		const formData = new FormData();
		formData.append('file', blobInfo.blob(), blobInfo.filename());

		try {
			const response = await directusClient.request(uploadFiles(formData));
			progress(100);
			return { location: route('cms_proxy', { cms_slug: `/assets/${response.id}` }) };
			return { location: route('cms_proxy', { cms_slug: `/assets/${response.id}` }) };
		} catch (error) {
			return Promise.reject({
				message: (error as any).message || 'Image upload failed',
				remove: true
			});
		}
	}

	const dispatch = createEventDispatcher();

	const advtemplate_templates = [
		{
			title: 'Schnelle Antworten',
			items: [
				{
					title: 'Nachricht erhalten',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}}!</p>\n<p dir="ltr">Nur eine kurze Notiz, um zu sagen, dass wir deine Nachricht erhalten haben und innerhalb von 48 Stunden auf dich zurückkommen werden.</p>\n<p dir="ltr">Zur Referenz, deine Ticketnummer ist: {{Ticket.Number}}</p>\n<p dir="ltr">Solltest du in der Zwischenzeit Fragen haben, antworte einfach auf diese E-Mail und sie wird diesem Ticket hinzugefügt.</p>\n<p><strong>&nbsp;</strong></p>\n<p dir="ltr">Grüße,</p>\n<p dir="ltr">{{Agent.FirstName}}</p>'
				},
				{
					title: 'Danke für das Feedback',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}},</p>\n<p dir="ltr">Wir danken dir, dass du dir die Zeit genommen hast, Feedback zu {{Product.Name}} zu geben.</p>\n<p dir="ltr">Es scheint, als hätte es deine Erwartungen nicht vollständig erfüllt, wofür wir uns entschuldigen. Sei versichert, dass unser Team jedes Feedback betrachtet und es nutzt, um zu entscheiden, worauf wir uns als Nächstes mit {{Product.Name}} konzentrieren werden.</p>\n<p dir="ltr"><strong>&nbsp;</strong></p>\n<p dir="ltr">Alles Gute und lass uns wissen, ob wir sonst noch etwas für dich tun können.</p>\n<p dir="ltr">-{{Agent.FirstName}}</p>'
				},
				{
					title: 'Arbeiten noch am Fall',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}},</p>\n<p dir="ltr">Nur eine kurze Notiz, um dich wissen zu lassen, dass wir noch an deinem Fall arbeiten. Es dauert etwas länger als wir gehofft haben, aber wir zielen darauf ab, dir innerhalb der nächsten 48 Stunden eine Antwort zu geben.</p>\n<p dir="ltr">Bleib dran,</p>\n<p dir="ltr">{{Agent.FirstName}}</p>'
				}
			]
		},
		{
			title: 'Tickets schließen',
			items: [
				{
					title: 'Ticket schließen',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}},</p>\n<p dir="ltr">Wir haben über eine Woche nichts von dir gehört, daher haben wir dein Ticketnummer {{Ticket.Number}} geschlossen.</p>\n<p dir="ltr">Wenn du immer noch auf Probleme stößt, mach dir keine Sorgen, antworte einfach auf diese E-Mail und wir werden dein Ticket wieder öffnen.</p>\n<p><strong>&nbsp;</strong></p>\n<p dir="ltr">Alles Gute,</p>\n<p dir="ltr">{{Agent.FirstName}}</p>'
				},
				{
					title: 'Nach-Anruf-Umfrage',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}}!</p>\n<p dir="ltr">&nbsp;</p>\n<p dir="ltr">Wie haben wir uns gemacht?</p>\n<p dir="ltr">Wenn du ein paar Momente Zeit hast, würden wir uns freuen, wenn du unsere Nach-Support-Umfrage ausfüllst: {{Survey.Link}}</p>\n<p><strong>&nbsp;</strong></p>\n<p dir="ltr">Danke im Voraus!<br>{{Company.Name}} Kundensupport</p>'
				}
			]
		},
		{
			title: 'Produktunterstützung',
			items: [
				{
					title: 'Wie man die Modellnummer findet',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}},</p>\n<p><strong>&nbsp;</strong></p>\n<p dir="ltr">Mein Name ist {{Agent.FirstName}} und ich werde dir heute gerne behilflich sein.</p>\n<p dir="ltr">Um dein Problem zu beheben, benötigen wir zuerst deine Modellnummer, die du auf der Unterseite deines Produkts unterhalb des Sicherheitshinweisschildes finden kannst.&nbsp;</p>\n<p dir="ltr">Sie sollte etwa so aussehen: XX.XXXXX.X</p>\n<p dir="ltr">Sobald du sie uns übermittelt hast, werde ich die nächsten Schritte beraten.</p>\n<p><strong>&nbsp;</strong></p>\n<p dir="ltr">Danke!</p>\n<p dir="ltr">{{Agent.FirstName}}</p>'
				},
				{
					title: 'Eskalation der Unterstützung',
					content:
						'<p dir="ltr">Hallo {{Customer.FirstName}},</p>\n<p dir="ltr">Wir haben dein Ticket {{Ticket.Number}} an die zweite Support-Ebene eskaliert.</p>\n<p dir="ltr">Du solltest bald von dem neuen Agenten in deinem Fall, {{NewAgent.FirstName}}, hören.</p>\n<p><strong>&nbsp;</strong></p>\n<p dir="ltr">Danke,</p>\n<p dir="ltr">{{Company.Name}} Kundensupport</p>'
				}
			]
		}
	];
	//@ts-ignore
	let editorInstance;
	let editorInitialized = false;

	// Keep track of our specific instance ID
	const editorId = `tinymce-${Math.random().toString(36).substring(2, 15)}`;

	// Add init options to ensure proper cleanup
	const conf = {
		plugins: [
			'advlist',
			'autolink',
			'link',
			'image',
			'lists',
			'charmap',
			'anchor',
			'searchreplace',
			'wordcount',
			'visualblocks',
			'visualchars',
			'advtable',
			'fullscreen',
			'insertdatetime',
			'media',
			'table',
			'emoticons',
			'codesample',
			'help',
			'accordion',
			'advtemplate'
		],
		menubar: editorMenuBar,
		toolbar: editorToolBar,
		image_advtab: true,
		paste_webkit_styles: 'all',
		paste_remove_styles_if_webkit: false,
		images_upload_handler: imageUploadHandler,
		content_style: 'body { line-height: 1; }',
		link_list: [
			{ title: 'My page 1', value: 'https://news.wekiwi.de/' },
			{ title: 'My page 2', value: 'https://www.digital-at-work.de/' }
		],
		image_list: [
			{ title: 'My page 1', value: 'https://www.google.de' },
			{ title: 'My page 2', value: 'http://www.kiel.de' }
		],
		image_class_list: [
			{ title: 'None', value: '' },
			{ title: 'Some class', value: 'class-name' }
		],
		advtemplate_templates,
		height: height,
		min_height: minHeight,
		min_width: minWidth,
		image_caption: true,
		quickbars_insert_toolbar: '',
		quickbars_selection_toolbar: 'bold italic | quicklink h2 h3 blockquote quickimage',
		noneditable_class: 'mceNonEditable',
		toolbar_mode: 'sliding',
		contextmenu: 'link',
		placeholder: placeholder,
		external_plugins: {
			chatPlugin: `${base}/editor/tinymce_ai_chat.js`,
			audioPlugin: `${base}/editor/tinymce_ai_audio.min.js`,
			mentionPlugin: `${base}/editor/tinymce_mentions.js`
		},
		mentionOptions: {
			mentionsList: circleUsers || [{ username: '', first_name: '', last_name: '' }],
			mentionsFilterOption(targetText: string, user: PartialUser) {
				const { username, first_name, last_name } = user;
				const lowerTarget = targetText.toLowerCase();
				return [username, first_name, last_name].some(
					(property) => property && property.toLowerCase().includes(lowerTarget)
				);
			}
		},
		chatPlugin: {
			getResponse: async function getResponseFromchatPlugin(prompt: string) {
				const requestBody = {
					model: 'gemma3:27b',
					prompt,
					stream: false
				};
				const headers: HeadersInit = {
					'Content-Type': 'application/json'
				};
				// API key is now handled server-side in the proxy
				const response = await fetch(route('ollama_proxy', { ollama_slug: 'api/generate' }), {
					method: 'POST',
					headers,
					body: JSON.stringify(requestBody)
				});
				return response;
			},
			prompts: [
				'Fasse den Text zusammen',
				'Formuliere den Text um',
				'Vereinfache den Text',
				'Korrigiere den Text',
				'Generiere eine Überschrift',
				'Schreibe einen Blogbeitrag',
				'Übersetze den Text ins Deutsche',
				'Übersetze den Text ins Englische',
				'Erstelle eine kritische Analyse',
				'Erstelle eine kurze Inhaltsangabe',
				'Identifiziere Schlüsselbegriffe',
				'Füge Beispiele hinzu',
				'Verbessere die Lesbarkeit',
				'Finde Argumente dafür und dagegen'
			]
		},
		audioPlugin: {
			getResponse: async function getResponse(audioBlob: Blob, editor: Editor) {
				const formData = new FormData();
				formData.append('audio', audioBlob);

				try {
					const response = await fetch('/audio=https://api.com/transcribe', {
						method: 'POST',
						body: formData
					});
					const data = await response.json();
					editor.insertContent(data.transcribedText);
				} catch (error) {
					console.error('Error sending audio to API:', error);
				}
			}
		},
		menu: {
			insert: { title: 'Insert', items: 'link emoticons codesample accordion hr template charmap' }
		},
		entity_encoding: 'named',
		valid_elements: `
			details[*],summary[*],p[style|align],strong/b,em/i,strike,u,sub,sup,code,codesample,pre,blockquote[style],h1,h2,h3,h4,h5,h6,
			ul,ol,li[style],br,span[style|class],
			img[src|alt|width|height|class|style|title|align|border|hspace|vspace|data-*],
			div[style|class],hr,align,caption
		`,
		extended_valid_elements: 'a[href|target|rel|title|class|style|id|data-*]',
		valid_styles: {
			'*': `color,font-size,font-family,font-weight,font-style,text-align,text-decoration,
				  background-color,border,border-radius,padding,margin,line-height,
				  width,height,max-width,max-height,vertical-align,white-space`,
			img: 'width,height,max-width,max-height,border,border-radius,vertical-align,hspace,vspace'
		},
		invalid_elements: 'table,thead,tbody,tfoot,tr,td,th',
		selector: `#${editorId}`,
		//@ts-ignore
		setup: (editor) => {
			// Add cleanup handler
			editor.on('remove', () => {
				editor.off('mentionSelected', boundMentionSelected);
				editor.off('mentionDeleted', boundMentionDeleted);
			});

			editor.on('init', () => {
				editorInitialized = true;
			});
		},
		//@ts-ignore
		init_instance_callback: (editor) => {
			editorInstance = editor;
		},
		//@ts-ignore
		remove_instance_callback: (editor) => {
			// Cleanup callback
		}
	} as any;
	//@ts-ignore
	function handleMentionSelected(e) {
		mentions = [...mentions, e.detail];
		dispatch('mentionsChange', mentions);
		console.log('Mention selected:', e.detail); // Debugging hinzufügen
	}
	//@ts-ignore
	function handleMentionDeleted(e) {
		mentions = mentions.filter((mention) => mention && mention.username !== e.detail.username);
		dispatch('mentionsChange', mentions);
		console.log('Mention deleted:', e.detail); // Debugging hinzufügen
	}

	const boundMentionSelected = handleMentionSelected.bind(null);
	const boundMentionDeleted = handleMentionDeleted.bind(null);

	//@ts-ignore
	function handleInit(e) {
		editorInstance = e.detail.editor;

		// Remove any existing handlers first
		editorInstance.off('mentionSelected', boundMentionSelected);
		editorInstance.off('mentionDeleted', boundMentionDeleted);

		// Add new handlers
		editorInstance.on('mentionSelected', boundMentionSelected);
		editorInstance.on('mentionDeleted', boundMentionDeleted);
	}

	onDestroy(() => {
		try {
			//@ts-ignore
			if (editorInstance?.initialized) {
				// Remove event listeners
				editorInstance.off('mentionSelected', boundMentionSelected);
				editorInstance.off('mentionDeleted', boundMentionDeleted);

				// Remove the editor instance using TinyMCE's global API
				if (window.tinymce) {
					window.tinymce.remove(`#${editorId}`);
				}
				editorInstance = null;
			}
		} catch (e) {
			console.error(`Error cleaning up TinyMCE instance:`, e);
		}
	});
</script>

<Editor
	id={editorId}
	scriptSrc={`${base}/editor/tinymce.min.js`}
	bind:cssClass={cssClasses}
	bind:text={textContent}
	bind:value={htmlContent}
	bind:disabled={readonly}
	on:init={handleInit}
	on:blur={() => dispatch('blur')}
	on:input={() => dispatch('input')}
	on:mentionSelected={handleMentionSelected}
	on:mentionDeleted={handleMentionDeleted}
	on:blur={() => dispatch('blur')}
	on:input={() => dispatch('input')}
	{inline}
	{conf}
	licenseKey="gpl"
/>

<style>
	:global(.oa-tinymce-mentions-container) {
		position: absolute;
		margin: 0;
		padding: 0;
		background-color: #ffffff !important;
		border-radius: 4px;
		width: 200px;
		z-index: 9999 !important;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
		overflow: auto;
	}

	:global(.oa-tinymce-mentions-list) {
		list-style: none;
		margin: 0;
		padding: 4px 0;
		background-color: #ffffff;
		background-color: #ffffff;
		max-height: 230px;
		box-sizing: border-box;
	}

	:global(.oa-tinymce-mention-item) {
		white-space: nowrap;
		text-overflow: ellipsis;
		overflow: hidden;
		cursor: pointer;
		margin: 0;
		padding: 9px 16px 9px 12px;
		color: #000000;
		font-size: 14px;
		line-height: 22px;
		transition: all linear 0.15s;
		background-color: #ffffff;
	}

	:global(.oa-tinymce-mention-item:hover) {
		background-color: rgba(0, 0, 0, 0.1);
		color: #4eb42f;
	}

	:global(.oa-tinymce-mention-item-active) {
		background-color: rgba(0, 0, 0, 0.1);
		color: #4eb42f;
	}

	:global(.remind-user) {
		color: #2f68b4;
	}

	:global(.tox-statusbar__right-container) {
		display: none !important;
	}
</style>

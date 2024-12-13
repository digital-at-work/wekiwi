import { writable, derived } from 'svelte/store';
import type { PartialContents } from '$lib/directus/directus.types';
import { getContext, setContext } from 'svelte';


function init() {
	const { subscribe, update } = writable(
		[] as PartialContents
	);

	const contents = { subscribe };

	const contentIds = derived(contents, ($contents: PartialContents) => {
		return $contents.map((obj) => obj.content_id);
	});

	/**
	 * Initializes the `contents` store with content root contents.
	 *
	 * @param results - An array of content objects to add.
	 */
	function initContents(contents: PartialContents | []) {
		console.log('initContents');
		update(() => {
			return contents;
		});
	}

	/**
	 * Adds content items to the `contents` store.
	 * 
	 * @param contents - An array of content objects to add.
	 */
	function addContents(contents: PartialContents) {
		console.log('addContents', contents);
		update((currentContents) => {
			return [...currentContents, ...contents];
		});
	}

	/**
	 * Modifies a content item in the `contents` store.
	 *
	 * @param content_id - The ID of the content item to modify.
	 * @param properties - The properties to update or add to the content item.
	 * @param parent_id - The ID of the parent content item (if applicable).
	 * @param mode - The modification mode ('update', 'add', or 'delete'). Defaults to 'update'.
	 *
	 * @returns True if the content item was found and modified, otherwise false.
	 */
	function modifyContent(
		content_id: number,
		properties: any = null,
		parent_id: number | null = null,
		mode: 'update' | 'add' | 'delete' = 'update'
	) {
		update((currentContents) => {
			if (mode === 'add' && parent_id === null) {
				for (let i = 0; i < currentContents.length; i++) {
					if (currentContents[i].content_id === content_id) {
						currentContents[i] = {
							...currentContents[i],
							...properties,
							content_id
						};
						return currentContents;
					}
				}

				currentContents.push({ ...properties, content_id });
				return currentContents;
			}

			updateContentRecursive(currentContents);
			return currentContents;

			function updateContentRecursive(contentsArray: any[]) {
				for (let i = 0; i < contentsArray.length; i++) {
					if (contentsArray[i].content_id === content_id) {
						switch (mode) {
							case 'add':
							case 'update':
								contentsArray[i] = { ...contentsArray[i], ...properties };
								break;
							case 'delete':
								contentsArray.splice(i, 1);
								break;
						}
						return true;
					}

					if (contentsArray[i].children && updateContentRecursive(contentsArray[i].children)) {
						return true;
					}

					if (mode === 'add' && contentsArray[i]?.content_id === parent_id) {
						contentsArray[i].children = contentsArray[i].children || [];
						contentsArray[i].children.push({
							...properties,
							content_id,
							parent_id
						});
						return true;
					}
				}
				return false;
			}
		});
	}

	return {
		contents,
		contentIds,
		modifyContent,
		initContents,
		addContents
	};
}

const key = Symbol();

export function setStateContext() {
	setContext(key, init());
}

export function getStateContext() {
	return getContext(key) as ReturnType<typeof init>;
}

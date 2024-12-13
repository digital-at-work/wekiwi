// eslint-disable-next-line no-undef
tinymce.PluginManager.add('mentionPlugin', function (editor) {
	// Initialize the MutationObserver that will listen for mentions being deleted

	editor.on('init', function () {
		const observer = new MutationObserver((mutations) => {
			mutations.forEach((mutation) => {
				mutation.removedNodes.forEach((node) => {
					// Check if the removed node is a mention span
					if (node.nodeType === 1 && node.matches && node.matches('span[data-remind-mention]')) {
						const mentionDetails = {
							id: node.getAttribute('data-remind-mention'),
							text: node.textContent
						};

						const mentionDeletedEvent = new CustomEvent('mentionDeleted', {
							detail: mentionDetails,
							bubbles: true,
							cancelable: true
						});
			
						editor.getElement().dispatchEvent(mentionDeletedEvent);

						// Dispatch custom event or handle the deletion
						console.log('Mention deleted:', mentionDetails);
					}
				});
			});
		});
		// Start observing changes in the editor's body
		observer.observe(editor.getBody(), { childList: true, subtree: true });

		// Store observer for potential cleanup later
		editor.mentionObserver = observer;
	});

	// Clean up observer when editor is removed
    editor.on('remove', function() {
        if (editor.mentionObserver) {
            editor.mentionObserver.disconnect();
        }
    });

	editor.on('keydown', (e) => {
		if (e.key === '@' || (e.key === 'Process' && e.shiftKey && e.code === 'Digit2')) {
			console.log('[MentionPlugin] Keydown event:', e);
			AutoComplete.getInstance(editor);
		}
	});
});

class AutoComplete {
	static instance;
	static isActive;
	static editor;
	static dropdown;
	static mentionStartIndex;
	id;

	constructor(editor) {
		this.editor = editor;
		this.id = Math.floor(Math.random() * 100000).toString();

		this.boundHandleKeydown = this.handleKeydown.bind(this);
		this.boundHandleKeyup = this.handleKeyup.bind(this);
		this.boundClearOnBlur = () => this.clear(true);
		this.bindEvents();

		AutoComplete.instance = this;
	}

	static getInstance(editor) {
		if (!this.instance) {
			console.log('[AutoComplete] Creating new instance');
			this.instance = new AutoComplete(editor);
		}
		console.log('[AutoComplete] Returning existing instance', this.instance);
		return this.instance;
	}

	getId() {
		return this.id;
	}

	bindEvents() {
		this.editor.on('keydown', this.boundHandleKeydown, true);
		this.editor.on('keyup', this.boundHandleKeyup);
		this.editor.on('blur', this.boundClearOnBlur);
	}

	unbindEvents() {
		this.editor.off('keydown', this.boundHandleKeydown, true);
		this.editor.off('keyup', this.boundHandleKeyup);
		this.editor.off('blur', this.boundClearOnBlur);
	}

	calcCurrentPosition(range, filterList) {
		const { x, y } = this.editor.editorContainer.getBoundingClientRect();
		const { x: rangeX, y: rangeY } = range.getBoundingClientRect();
		const [domWidth, domHeight] = [200, Math.min(40 * filterList.length + 16, 230)];

		let [top, left] = [y + rangeY + 20, x + rangeX + 10];
		if (top + domHeight > window.innerHeight) top -= domHeight + 20;
		if (left + domWidth > window.innerWidth) left -= domWidth;

		return { top, left };
	}

	createListItem(user, idx) {
		const li = document.createElement('li');
		li.className = `oa-tinymce-mention-item ${idx === 0 ? 'oa-tinymce-mention-item-active' : ''}`;
		li.dataset.idx = idx.toString();
		li.dataset.username = user.username;
		li.innerText = `${user.first_name || ''} ${user.last_name || ''} - ${user.username}`;
		li.addEventListener('mousedown', () => this.selectActiveItem(li));
		return li;
	}

	updateDropdown(filterList, position) {
		if (!this.dropdown) {
			console.log('[AutoComplete] Creating dropdown');
			this.dropdown = document.createElement('div');
			this.dropdown.className = 'oa-tinymce-mention-container';
			document.body.appendChild(this.dropdown);
		}

		this.dropdown.innerHTML = '';
		this.dropdown.style.top = `${position.top}px`;
		this.dropdown.style.left = `${position.left}px`;

		const ul = document.createElement('ul');
		ul.className = 'oa-tinymce-mention-list';
		ul.dataset.size = filterList.length.toString();

		filterList.forEach((item, idx) => ul.appendChild(this.createListItem(item, idx)));

		this.dropdown.appendChild(ul);
	}

	selectActiveItem(active) {
		const { username } = active.dataset;

		if (this.mentionStartIndex != null && this.mentionStartIndex >= 0) {
			const range = this.editor.selection.getRng();
			range.setStart(range.startContainer, this.mentionStartIndex);
			range.deleteContents();

			// Dispatch custom event
			const mentionSelectedEvent = new CustomEvent('mentionSelected', {
				detail: { id: this.id, username: username },
				bubbles: true,
				cancelable: true
			});

			this.editor.getElement().dispatchEvent(mentionSelectedEvent);
			console.log('Mention selected:', { id: this.id, username });

			// Insert the mention
			this.editor.execCommand(
				'mceInsertContent',
				false,
				`<span data-remind-mention="${this.id}" contenteditable="false" style="color: #2f68b4;">&nbsp;@${username}&nbsp;</span>`
			);

			this.clear(true);
		}
	}

	highlightItem(direction) {
		if (!this.dropdown) return;

		const ul = this.dropdown.querySelector('ul.oa-tinymce-mention-list');
		const active = this.dropdown.querySelector('li.oa-tinymce-mention-item-active');
		let nextIdx = active ? Number(active.dataset.idx) + direction : 0;
		const size = Number(ul.dataset.size);

		if (nextIdx < 0) nextIdx = size - 1;
		if (nextIdx >= size) nextIdx = 0;

		if (active) active.classList.remove('oa-tinymce-mention-item-active');
		ul.children[nextIdx].classList.add('oa-tinymce-mention-item-active');
	}

	handleKeydown(e) {
		switch (e.key) {
			case 'Enter':
			case 'Escape':
				e.preventDefault();
				break;
			case 'ArrowUp':
			case 'ArrowDown':
			case 'ArrowLeft':
			case 'ArrowRight':
				e.preventDefault();
				if (e.key === 'ArrowUp') this.highlightItem(-1);
				if (e.key === 'ArrowDown') this.highlightItem(1);
				break;
		}
		console.log('handleKeydown');
		e.stopPropagation();
	}

	handleKeyup(e) {
		if (['Shift', 'Control', 'Alt', 'ArrowUp', 'ArrowDown'].includes(e.key)) {
			e.preventDefault();
		} else if (['ArrowLeft', 'ArrowRight'].includes(e.key)) {
			this.hide();
			//e.preventDefault();
		} else if (e.key === 'Enter') {
			const active = this.dropdown?.querySelector('li.oa-tinymce-mention-item-active');
			active ? this.selectActiveItem(active) : this.clear();
		} else if (e.key === 'Escape') {
			this.clear();
		} else if (e.key === 'Delete') {
			console.log('delete');
		} else {
			console.log('lookup');
			this.lookup();
		}
	}

	lookup() {
		// Access the range and content with minimal operations
		const range = this.editor.selection.getRng();
		const content = range.startContainer.textContent || '';
		const endOffset = range.endOffset;
		const lastAtIndex = content.lastIndexOf('@', endOffset);

		// Directly slice the target text
		const targetText = content.slice(lastAtIndex + 1, endOffset).replace('\ufeff', '');

		// Return early if no '@' found
		if (lastAtIndex === -1) {
			this.hide();
			return;
		}

		if (lastAtIndex >= 0) {
			this.mentionStartIndex = lastAtIndex;
		}

		const { mentionsList, mentionsFilterOption } = this.editor.getParam('mentionOptions');
		const filterList = mentionsList.filter((i) =>
			mentionsFilterOption(targetText, i)
		);

		// Show or hide based on the target text and filter list
		if (targetText && filterList.length > 0) {
			this.show(filterList, range);
			this.isActive = true;
		} else {
			this.hide();
		}
	}

	show(filterList, range) {
		const position = this.calcCurrentPosition(range, filterList);
		this.updateDropdown(filterList, position);
	}

	getDomValue(el) {
		return Array.from(el.childNodes)
			.map((child) =>
				child.nodeName === '#text'
					? child.nodeValue
					: child.nodeName === 'SPAN'
					? this.getDomValue(child)
					: ''
			)
			.join('');
	}

	clear(async = false) {
		if (async) {
			Promise.resolve().then(() => {
				this.unbindEvents();
				if (this.dropdown) document.body.removeChild(this.dropdown);
				this.dropdown = null;
			});
		} else {
			this.unbindEvents();
			if (this.dropdown) document.body.removeChild(this.dropdown);
			this.dropdown = null;
		}
		AutoComplete.instance = undefined;
	}

	hide() {
		if (this.dropdown && document.body.contains(this.dropdown)) {
			document.body.removeChild(this.dropdown);
			this.dropdown = null;
		}
	}
}
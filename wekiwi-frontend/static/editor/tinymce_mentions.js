tinymce.PluginManager.add('mentionPlugin', function (editor) {
    let isProcessingChange = false;

    // Constants
    const GUARD_CLASS = 'mention-guard';
    const MENTION_HIGHLIGHT_CLASS = 'mention-highlight';
    const ZERO_WIDTH_SPACE = '\u200B';

    // Add editor styles for mentions
    editor.on('init', function() {
        const css = `
            .mention.${MENTION_HIGHLIGHT_CLASS} {
                background-color: #d3edff;
                border: 1px solid #1890ff;
                border-radius: 4px;
                padding: 2px 4px;
                text-decoration: none;
                white-space: nowrap;
            }
            .${GUARD_CLASS} {
                display: inline-block;
                width: 0;
                overflow: hidden;
            }
        `;
        editor.dom.addStyle(css);
    });

    editor.on('keydown', (e) => {
        if (e.key === '@') {
            AutoComplete.getInstance(editor);
        }
    });

    // Function to find the associated mention for a guard node
    function findMentionForGuard(guardNode) {
        const prevSibling = guardNode.previousSibling;
        if (prevSibling && prevSibling.classList && prevSibling.classList.contains('mention')) {
            return prevSibling;
        }
        return null;
    }

    // Function to find the associated guard for a mention node
    function findGuardForMention(mentionNode) {
        const nextSibling = mentionNode.nextSibling;
        if (nextSibling && nextSibling.classList && nextSibling.classList.contains(GUARD_CLASS)) {
            return nextSibling;
        }
        return null;
    }

    // Function to create a guard node
    function createGuardNode() {
        const guard = editor.getDoc().createElement('span');
        guard.className = GUARD_CLASS;
        guard.contentEditable = 'false';
        guard.innerHTML = ZERO_WIDTH_SPACE;
        return guard;
    }

    // Function to create a mention node with its guard
    function createMentionWithGuard(username) {
        const wrapper = editor.getDoc().createDocumentFragment();
        const mention = editor.getDoc().createElement('span');
        mention.className = `mention ${MENTION_HIGHLIGHT_CLASS}`;
        mention.contentEditable = 'false';
        mention.setAttribute('data-username', username);
        mention.textContent = `@${username}`;
        
        const guard = createGuardNode();
        
        wrapper.appendChild(mention);
        wrapper.appendChild(guard);
        return wrapper;
    }

    // Function to check if text matches a valid mention format
    function isValidMention(text, username) {
        return text === `@${username}`;
    }

    // Function to get user data from username
    function getUserData(username) {
        const mentionOptions = editor.getParam('mentionOptions', {});
        const mentionsList = mentionOptions.mentionsList || [];
        return mentionsList.find(user => user.username === username);
    }

    // Function to calculate cursor offset within a node
    function getOffsetInNode(node, range) {
        if (node === range.startContainer) {
            return range.startOffset;
        }
        
        let offset = 0;
        let currentNode = node.firstChild;
        
        while (currentNode) {
            if (currentNode === range.startContainer) {
                return offset + range.startOffset;
            }
            offset += currentNode.textContent.length;
            currentNode = currentNode.nextSibling;
        }
        
        return offset;
    }

    // Function to handle mention deletion/conversion
    function handleMentionInvalidation(mentionSpan) {
        const username = mentionSpan.getAttribute('data-username');
        if (!username) return;

        const userData = getUserData(username);
        if (!userData) return;

        // Store current selection state
        const selection = editor.selection;
        const range = selection.getRng();
        const isInMention = mentionSpan.contains(range.startContainer);
        const offsetInMention = isInMention ? getOffsetInNode(mentionSpan, range) : 0;
        
        // Get reference nodes
        const parentNode = mentionSpan.parentNode;
        const guardNode = findGuardForMention(mentionSpan);
        const nextSibling = guardNode ? guardNode.nextSibling : mentionSpan.nextSibling;

        // Remove highlight class before firing event
        mentionSpan.classList.remove(MENTION_HIGHLIGHT_CLASS);

        // Fire the deletion event
        editor.fire('mentionDeleted', {
            detail: userData
        });

        // Convert to plain text
        const textContent = mentionSpan.textContent;
        const textNode = editor.getDoc().createTextNode(textContent);
        
        // Replace the mention span with text node
        parentNode.replaceChild(textNode, mentionSpan);
        
        // Remove the guard if it exists
        if (guardNode) {
            guardNode.remove();
        }

        // Restore cursor position
        const newRange = editor.getDoc().createRange();
        
        if (isInMention) {
            // If cursor was inside the mention, place it at the same offset in the text node
            newRange.setStart(textNode, Math.min(offsetInMention, textContent.length));
            newRange.setEnd(textNode, Math.min(offsetInMention, textContent.length));
        } else if (range.startContainer === parentNode) {
            // If cursor was in the parent node
            let newOffset = range.startOffset;
            if (range.startOffset > Array.from(parentNode.childNodes).indexOf(textNode)) {
                newOffset--; // Adjust for removed span
            }
            newRange.setStart(parentNode, newOffset);
            newRange.setEnd(parentNode, newOffset);
        } else if (nextSibling && range.startContainer === nextSibling) {
            // If cursor was in the next sibling
            newRange.setStart(range.startContainer, range.startOffset);
            newRange.setEnd(range.endContainer, range.endOffset);
        } else {
            // Keep the original range for all other cases
            newRange.setStart(range.startContainer, range.startOffset);
            newRange.setEnd(range.endContainer, range.endOffset);
        }

        // Apply the new range
        selection.setRng(newRange);
    }

    // Monitor changes to mention spans
    editor.on('NodeChange', function(e) {
        if (isProcessingChange) return;
        isProcessingChange = true;

        try {
            const mentions = editor.getBody().getElementsByClassName('mention');
            const range = editor.selection.getRng();
            
            // Validate range first
            if (!range || !range.startContainer || !range.startContainer.nodeType) {
                return;
            }

            // Collect mentions to remove in a separate pass
            const mentionsToRemove = [];
            
            Array.from(mentions).forEach((mentionSpan) => {
                // Safety check for mention span
                if (!mentionSpan || !mentionSpan.parentNode || !editor.getBody().contains(mentionSpan)) {
                    return;
                }

                const username = mentionSpan.getAttribute('data-username');
                if (!username) return;

                // Ensure mention has a guard
                if (!findGuardForMention(mentionSpan)) {
                    const guard = createGuardNode();
                    if (mentionSpan.nextSibling) {
                        mentionSpan.parentNode.insertBefore(guard, mentionSpan.nextSibling);
                    } else {
                        mentionSpan.parentNode.appendChild(guard);
                    }
                }

                // Safely check if cursor is inside mention
                let isCursorInsideMention = false;
                try {
                    isCursorInsideMention = mentionSpan.contains(range.startContainer);
                } catch (err) {
                    return;
                }

                // Only validate if cursor is inside the mention
                if (isCursorInsideMention && !isValidMention(mentionSpan.textContent, username)) {
                    mentionsToRemove.push(mentionSpan);
                }
            });

            // Remove invalid mentions in a separate pass
            mentionsToRemove.forEach(mentionSpan => {
                if (mentionSpan && mentionSpan.parentNode) {
                    handleMentionInvalidation(mentionSpan);
                }
            });
        } catch (err) {
        } finally {
            isProcessingChange = false;
        }
    });

    // Handle mention deletion via backspace/delete
    editor.on('keydown', function(e) {
        if (e.key === 'Backspace' || e.key === 'Delete') {
            const selection = editor.selection;
            const range = selection.getRng();
            
            // Safety check for range
            if (!range || !range.startContainer || !range.startContainer.nodeType) {
                return;
            }
            
            // Get the element that's about to be deleted
            let elementToDelete = null;
            
            try {
                // Case 1: If selection is collapsed and at start of text node (for Backspace)
                if (e.key === 'Backspace' && range.collapsed && range.startContainer.nodeType === 3 && range.startOffset === 0) {
                    const prevSibling = range.startContainer.previousSibling;
                    if (prevSibling && prevSibling.nodeType === 1) { // Element node
                        if (prevSibling.classList.contains('mention')) {
                            elementToDelete = prevSibling;
                        } else if (prevSibling.classList.contains(GUARD_CLASS)) {
                            elementToDelete = findMentionForGuard(prevSibling);
                        }
                    }
                }
                
                // Case 2: If selection is collapsed and at end of text node (for Delete)
                if (e.key === 'Delete' && range.collapsed && range.startContainer.nodeType === 3 && range.startOffset === range.startContainer.length) {
                    const nextSibling = range.startContainer.nextSibling;
                    if (nextSibling && nextSibling.nodeType === 1) { // Element node
                        if (nextSibling.classList.contains('mention')) {
                            elementToDelete = nextSibling;
                        } else if (nextSibling.classList.contains(GUARD_CLASS)) {
                            elementToDelete = findMentionForGuard(nextSibling);
                        }
                    }
                }
                
                // Case 3: If cursor is inside or at boundaries of a mention or guard
                const selectedNode = selection.getNode();
                if (selectedNode && selectedNode.nodeType === 1) { // Element node
                    if (selectedNode.classList.contains('mention')) {
                        elementToDelete = selectedNode;
                    } else if (selectedNode.classList.contains(GUARD_CLASS)) {
                        elementToDelete = findMentionForGuard(selectedNode);
                    }
                }

                // Case 4: If there's a selection range that includes a mention
                if (!range.collapsed) {
                    const mentions = editor.getBody().getElementsByClassName('mention');
                    for (const mention of mentions) {
                        try {
                            if (range.intersectsNode(mention)) {
                                elementToDelete = mention;
                                break;
                            }
                        } catch (err) {
                        }
                    }
                }

                // If we found a mention to delete and it's still valid
                if (elementToDelete && elementToDelete.parentNode && editor.getBody().contains(elementToDelete)) {
                    handleMentionInvalidation(elementToDelete);
                    e.preventDefault();
                }
            } catch (err) {
            }
        }
    });

    // Add guards to mentions when content is set
    editor.on('SetContent', function() {
        const mentions = editor.getBody().getElementsByClassName('mention');
        Array.from(mentions).forEach(mention => {
            mention.contentEditable = 'false';
            mention.classList.add(MENTION_HIGHLIGHT_CLASS);
            if (!findGuardForMention(mention)) {
                const guard = createGuardNode();
                if (mention.nextSibling) {
                    mention.parentNode.insertBefore(guard, mention.nextSibling);
                } else {
                    mention.parentNode.appendChild(guard);
                }
            }
        });
    });

    editor.on('remove', function () {
        if (AutoComplete.instance) {
            AutoComplete.instance.clear();
        }
    });
});

class AutoComplete {
    static instance = null;

    constructor(editor) {
        this.editor = editor;
        this.dropdown = null;
        this.mentionStartIndex = null;
        this.boundHandleKeydown = this.handleKeydown.bind(this);
        this.boundHandleKeyup = this.handleKeyup.bind(this);
        this.boundHandleDocumentClick = this.handleDocumentClick.bind(this);

        this.bindEvents();
    }

    static getInstance(editor) {
        if (this.instance) {
            this.instance.clear();
        }
        this.instance = new AutoComplete(editor);
        return this.instance;
    }

    bindEvents() {
        this.editor.on('keydown', this.boundHandleKeydown);
        this.editor.on('keyup', this.boundHandleKeyup);
        document.addEventListener('click', this.boundHandleDocumentClick);
    }

    unbindEvents() {
        this.editor.off('keydown', this.boundHandleKeydown);
        this.editor.off('keyup', this.boundHandleKeyup);
        document.removeEventListener('click', this.boundHandleDocumentClick);
    }

    handleDocumentClick(event) {
        if (!this.dropdown) return;
        if (!this.dropdown.contains(event.target)) {
            this.clear();
        }
    }

    handleKeydown(e) {
        if (this.dropdown) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                e.preventDefault();
                this.navigateDropdown(e.key === 'ArrowDown' ? 1 : -1);
            } else if (e.key === 'Escape') {
                this.clear();
            }
        }
    }

    handleKeyup(e) {
        if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp' && e.key !== 'Enter' && e.key !== 'Escape') {
            this.lookup();
        }
    }

    lookup() {
        const range = this.editor.selection.getRng();
        const content = range.startContainer.textContent || '';
        const atSymbolIndex = content.lastIndexOf('@');
    
        if (atSymbolIndex === -1) {
            this.clear();
            return;
        }
    
        this.mentionStartIndex = atSymbolIndex;
        const targetText = content.slice(atSymbolIndex + 1, range.endOffset).trim();

        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$/;
        const fullText = content.slice(0, range.endOffset);

        if (emailPattern.test(fullText)) {
            this.clearDropdownOnly();
            return;
        }

        const mentionOptions = this.editor.getParam('mentionOptions', {});
        const mentionsList = mentionOptions.mentionsList || [];
        const mentionsFilterOption = mentionOptions.mentionsFilterOption || (() => true);

        const filteredList = mentionsList.filter((user) =>
            mentionsFilterOption(targetText, user)
        );

        if (filteredList.length > 0) {
            this.showDropdown(filteredList, range);
        } else {
            this.clearDropdownOnly();
        }
    }

    clearDropdownOnly() {
        if (this.dropdown) {
            document.body.removeChild(this.dropdown);
            this.dropdown = null;
        }
        this.unbindEvents();
    }

    showDropdown(users, range) {
        if (!this.dropdown) {
            this.dropdown = document.createElement('div');
            this.dropdown.className = 'oa-tinymce-mention-container';
            document.body.appendChild(this.dropdown);
        }

        this.dropdown.innerHTML = '';
        this.positionDropdown(range);

        users.forEach((user, idx) => {
            const item = document.createElement('div');
            item.className = 'oa-tinymce-mention-item' + (idx === 0 ? ' oa-tinymce-mention-item-active' : '');
            item.dataset.username = user.username;
            item.innerText = `${user.first_name} ${user.last_name} (@${user.username})`;

            item.addEventListener('mousedown', (event) => {
                event.preventDefault();
                this.selectItem(item);
            });

            this.dropdown.appendChild(item);
        });
    }

    positionDropdown(range) {
        const editorContainerRect = this.editor.getContainer().getBoundingClientRect();
        const rangeRect = range.getBoundingClientRect();

        this.dropdown.style.position = 'absolute';
        this.dropdown.style.left = `${window.scrollX + editorContainerRect.left + rangeRect.left}px`;
        this.dropdown.style.top = `${window.scrollY + editorContainerRect.top + rangeRect.bottom}px`;
        this.dropdown.style.width = '200px';
        this.dropdown.style.zIndex = '10000';
    }

    navigateDropdown(direction) {
        const items = this.dropdown.querySelectorAll('.oa-tinymce-mention-item');
        const activeItem = this.dropdown.querySelector('.oa-tinymce-mention-item-active');
        let nextIdx = Array.from(items).indexOf(activeItem) + direction;

        if (nextIdx < 0) nextIdx = items.length - 1;
        if (nextIdx >= items.length) nextIdx = 0;

        if (activeItem) activeItem.classList.remove('oa-tinymce-mention-item-active');
        items[nextIdx].classList.add('oa-tinymce-mention-item-active');
    }

    selectItem(item) {
        const username = item.dataset.username;
        this.isMentionSelected = true;

        const range = this.editor.selection.getRng();
        const content = range.startContainer.textContent || '';

        if (this.mentionStartIndex !== null && this.mentionStartIndex >= 0) {
            const beforeMention = content.slice(0, this.mentionStartIndex);
            const afterCursor = content.slice(range.endOffset);

            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+$/;
            if (emailPattern.test(beforeMention.trimEnd())) {
                this.clear();
                return;
            }

            const mentionHTML = `<span contenteditable="false" class="mention mention-highlight" data-username="${username}">@${username}</span>&nbsp;`;

            const updatedContent = beforeMention + mentionHTML + afterCursor;
            range.startContainer.textContent = '';
            this.editor.selection.setContent(updatedContent);

            // Get the user data from mentionOptions
            const mentionOptions = this.editor.getParam('mentionOptions', {});
            const mentionsList = mentionOptions.mentionsList || [];
            const userData = mentionsList.find(user => user.username === username);

            if (userData) {
                // Dispatch mention selected event with full user data
                this.editor.fire('mentionSelected', {
                    detail: userData
                });
            }

            try {
                // Set cursor position after the mention
                const newRange = this.editor.selection.getRng();
                const spans = this.editor.getBody().getElementsByClassName('mention');
                const lastSpan = spans[spans.length - 1];
                if (lastSpan && lastSpan.nextSibling) {
                    newRange.setStartAfter(lastSpan);
                    newRange.collapse(true);
                    this.editor.selection.setRng(newRange);
                }
            } catch (err) {
            }
        }

        this.clear();
    }
    
    clear() {
        if (this.dropdown) {
            document.body.removeChild(this.dropdown);
            this.dropdown = null;
        }

        if (!this.isMentionSelected && this.mentionStartIndex !== null && this.mentionStartIndex >= 0) {
            const range = this.editor.selection.getRng();
            const content = range.startContainer.textContent || '';

            if (content) {
                const updatedContent =
                    content.slice(0, this.mentionStartIndex) + content.slice(this.mentionStartIndex + 1);

                range.startContainer.textContent = updatedContent;

                try {
                    this.editor.selection.setCursorLocation(range.startContainer, this.mentionStartIndex);
                } catch (err) {
                }
            }
        }

        this.unbindEvents();
        this.isMentionSelected = false;
        AutoComplete.instance = null;
    }
}

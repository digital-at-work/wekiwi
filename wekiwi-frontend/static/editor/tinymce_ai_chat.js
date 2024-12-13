// eslint-disable-next-line no-undef
tinymce.PluginManager.add('chatPlugin', function (editor) {
    const chatPlugin = editor.getParam('chatPlugin')
  
    const openDialog = function () {
      const PROMPTS = chatPlugin.prompts
        ? chatPlugin.prompts.map((prompt) => {
          return { text: prompt, value: `You are a HELPFUL assistant that responds in GERMAN (unless specified differently). You STRICTLY complete the TASK based on the INPUT (CONSIZE). TASK: ${prompt} INPUT: ` }
        })
        : []
      PROMPTS.unshift({ text: 'Custom Prompt', value: '' })
  
      return editor.windowManager.open({
        title: 'AI Text Helper',
        body: {
          type: 'panel',
          items: [
            {
              type: 'textarea',
              name: 'inputText',
              label: 'Gebe hier deinen Text ein',
            },
            {
              type: 'selectbox',
              name: 'prompt',
              label: 'Wähle ein Prompt aus',
              items: PROMPTS
            },
            {
              type: 'htmlpanel',
              html: '<p style="font-size: 11px;text-align: center;margin-top:12px;"></p>'
            }
          ]
        },
        buttons: [
          {
            type: 'cancel',
            text: 'Schließen'
          },
          {
            type: 'submit',
            text: 'Generieren',
            primary: true
          }
        ],
  
        initialData: {
          // eslint-disable-next-line no-undef
          inputText: tinymce.activeEditor.selection.getContent() ?? ''
        },
  
        onSubmit: function (api) {
          api.block('Bitte warte kurz ...')
  
          const data = api.getData()
          const input = data.inputText
          let prompt = data.prompt ?? '' 
          prompt += `${input} ### RESPONSE:`
  
          chatPlugin.getResponse(prompt)
            .then((res) => res.json())
            .then((data) => {
              const reply = data.completions[0].completion
              editor.insertContent(reply)
              api.close()
            })
            .catch((error) => {
              console.log('The following error occoured in the chat plugin ' + error)
            })
        }
      })
    }
  
    editor.ui.registry.addIcon(
      'chatPlugin',
      `<svg width="30px" height="30px" viewBox="0 0 76 76" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" baseProfile="full" enable-background="new 0 0 76.00 76.00" xml:space="preserve" fill="#000000">
        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
        <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
        <g id="SVGRepo_iconCarrier">
            <path fill="#000000" fill-opacity="1" stroke-width="0.2" stroke-linejoin="round" 
              d="M 30.4822,22.8009L 37.3426,22.8009L 46.9122,52.2525L 41.1446,52.2525L 38.4785,43.9062L 29.1276,43.9062L 26.5929,52.2525L 21.0439,52.2525L 30.4822,22.8009 Z 
                 M 32.2736,32.5887L 30.0017,39.8432L 37.5616,39.8432L 35.2452,32.5887C 34.6774,30.7977 34.1965,28.7872 33.7601,27.083L 33.6723,27.083C 33.2351,28.7872 32.7982,30.8409 32.2736,32.5887 Z 
                 M 48.7023,25.0292C 48.7023,23.3687 49.9255,22.1014 51.717,22.1014C 53.5521,22.1014 54.6885,23.3687 54.7322,25.0292C 54.7322,26.6462 53.5521,27.9135 51.6733,27.9135C 49.8819,27.9135 48.7023,26.6462 48.7023,25.0292 Z 
                 M 49.0077,52.2525L 49.0077,30.9723L 54.4267,30.9723L 54.4267,52.2525L 49.0077,52.2525 Z ">
            </path>
        </g>
      </svg>`
    )
  
    editor.ui.registry.addButton('chatPlugin', {
      icon: 'chatPlugin',
      tooltip: 'AI TextHelper',
      onAction: function () {
        openDialog()
      }
    })
  
    editor.ui.registry.addMenuItem('chatPlugin', {
      text: 'AI TextHelper',
      onAction: function () {
        openDialog()
      }
    })
  
    return {
      getMetadata: function () {
        return {
          name: 'AI Chat Plugin',
        }
      }
    }
  })
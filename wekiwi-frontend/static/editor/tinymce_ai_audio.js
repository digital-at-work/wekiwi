// eslint-disable-next-line no-undef
tinymce.PluginManager.add('audioPlugin', function (editor) {
	let mediaRecorder;
	let recordButton;
	let audioChunks = [];
	let stream;
	let isRecording = false;

	async function initRecorder() {
		stream = await navigator.mediaDevices.getUserMedia({ audio: true });
		mediaRecorder = new MediaRecorder(stream);

		mediaRecorder.ondataavailable = (event) => {
			audioChunks.push(event.data);
		};

		mediaRecorder.onstop = async () => {
			const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
			audioChunks = [];
			// callback function for chatPlugin that returns the response from the API and inserts it into the editor
			await editor.getParam('chatPlugin').getResponse(audioBlob, editor);
		};
	}

	function startRecording() {
		audioChunks = [];
		mediaRecorder.start();
		isRecording = true;
		updateButtonAppearance();
	}

	function stopRecording() {
		mediaRecorder.stop();
		isRecording = false;
		updateButtonAppearance();
	}

	function updateButtonAppearance() {
		if (isRecording) {
			recordButton.setIcon('stopRecord');
			recordButton.setText('Stop Recording');
		} else {
			recordButton.setIcon('startRecord');
			recordButton.setText('Record Audio');
		}
	}

	editor.ui.registry.addIcon(
		'startRecord',
		'<svg height="16" width="16" viewBox="0 0 384 512"><path fill="#d01c1c" d="M96 96V256c0 53 43 96 96 96s96-43 96-96H208c-8.8 0-16-7.2-16-16s7.2-16 16-16h80V192H208c-8.8 0-16-7.2-16-16s7.2-16 16-16h80V128H208c-8.8 0-16-7.2-16-16s7.2-16 16-16h80c0-53-43-96-96-96S96 43 96 96zM320 240v16c0 70.7-57.3 128-128 128s-128-57.3-128-128V216c0-13.3-10.7-24-24-24s-24 10.7-24 24v40c0 89.1 66.2 162.7 152 174.4V464H120c-13.3 0-24 10.7-24 24s10.7 24 24 24h72 72c13.3 0 24-10.7 24-24s-10.7-24-24-24H216V430.4c85.8-11.7 152-85.3 152-174.4V216c0-13.3-10.7-24-24-24s-24 10.7-24 24v24z"/></svg>'
	);

	editor.ui.registry.addIcon(
		'stopRecord',
		'<svg height="16" width="16" viewBox="0 0 640 512"><path fill="#d01c1c" d="M38.8 5.1C28.4-3.1 13.3-1.2 5.1 9.2S-1.2 34.7 9.2 42.9l592 464c10.4 8.2 25.5 6.3 33.7-4.1s6.3-25.5-4.1-33.7L472.1 344.7c15.2-26 23.9-56.3 23.9-88.7V216c0-13.3-10.7-24-24-24s-24 10.7-24 24v24 16c0 21.2-5.1 41.1-14.2 58.7L416 300.8V256H358.9l-34.5-27c2.9-3.1 7-5 11.6-5h80V192H336c-8.8 0-16-7.2-16-16s7.2-16 16-16h80V128H336c-8.8 0-16-7.2-16-16s7.2-16 16-16h80c0-53-43-96-96-96s-96 43-96 96v54.3L38.8 5.1zM358.2 378.2C346.1 382 333.3 384 320 384c-70.7 0-128-57.3-128-128v-8.7L144.7 210c-.5 1.9-.7 3.9-.7 6v40c0 89.1 66.2 162.7 152 174.4V464H248c-13.3 0-24 10.7-24 24s10.7 24 24 24h72 72c13.3 0 24-10.7 24-24s-10.7-24-24-24H344V430.4c20.4-2.8 39.7-9.1 57.3-18.2l-43.1-33.9z"/></svg>'
	);

	editor.ui.registry.addButton('audioPlugin', {
		icon: 'startRecord',
		tooltip: 'Record Audio',
		onSetup: function (api) {
			recordButton = api;
			return function () {
				if (isRecording) {
					stopRecording();
				}
				if (stream) {
					stream.getTracks().forEach((track) => track.stop());
				}
			};
		},
		onAction: function () {
			if (!isRecording) {
				initRecorder().then(startRecording);
			} else {
				stopRecording();
			}
		}
	});

	editor.ui.registry.addMenuItem('audioRecorderPlugin', {
		text: 'Record Audio',
		onAction: function () {
			if (!isRecording) {
				initRecorder().then(startRecording);
			} else {
				stopRecording();
			}
		}
	});

	return {
		getMetadata: function () {
			return {
				name: 'Audio Recorder Plugin'
			};
		}
	};
});

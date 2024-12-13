<!-- <script lang="ts">
    import { audioRecorder } from '$lib/components/audio/audiorecorder';
    let isRecording = false;
    let audioFiles: File[];
  
    function handleStart() {
      isRecording = true;
    }
  
    function handleStop(blob: BlobPart) {
      isRecording = false;
      audioFiles = [new File([blob], "recording.wav", { type: 'audio/wav' })];
    }
  </script>
  
  <div use:audioRecorder={{ onStart: handleStart, onStop: handleStop }}>
    {#if isRecording}
      <button on:click={() => audioRecorder.stop()}>Stop Recording</button>
    {:else}
      <button on:click={() => audioRecorder.start()}>Start Recording</button>
    {/if}
  
    {#if audioFiles}
      <form action="/api/submitAudio" method="post" enctype="multipart/form-data">
        <input type="file" id="audioFileInput" name="audio" hidden bind:files={audioFiles}>
        <button type="submit">Submit Recording</button>
      </form>
    {/if}
  </div>
   -->
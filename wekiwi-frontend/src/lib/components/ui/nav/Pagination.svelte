<script lang="ts">
  export let pages: number;
  export let p: number;
  export let href: (p: number) => string;

  let range: number[];

  $: {
    range = [];
    if (pages > 1) {
      for (let i = 1; i <= pages; ++i) {
        range.push(i);
      }
    }
  }
</script>

{#if pages > 1}
  <nav>
    <ul class="pagination">
      {#each range as n}
        <li class="page-item" class:active={n == p}>
          <a class="page-link" href={href(n)}>{n}</a>
        </li>
      {/each}
    </ul>
  </nav>
{/if}

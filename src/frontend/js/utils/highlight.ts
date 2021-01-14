import hljs from 'highlight.js';

export const renderHighlight = () => {
  document.querySelectorAll('.post-content pre code').forEach((block) => {
    if (block instanceof HTMLElement) {
      hljs.highlightBlock(block);
    }
  });
};

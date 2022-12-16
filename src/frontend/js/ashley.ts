import { renderEmojis } from './utils/emojis';
import { renderHighlight } from './utils/highlight';
import { renderLatex } from './utils/latex';

// expose some modules to the global window object

document.addEventListener('DOMContentLoaded', (event) => {
  renderEmojis();
  renderHighlight();
  renderLatex();
});

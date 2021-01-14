import { init } from './components/AshleyEditor';
import { renderEmojis } from './utils/emojis';
import { renderHighlight } from './utils/highlight';

// expose some modules to the global window object
declare var window: any;
window.Ashley = {
  Editor: {
    init,
  },
};

document.addEventListener('DOMContentLoaded', (event) => {
  renderEmojis();
  renderHighlight();
});

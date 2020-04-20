import * as AshleyEditor from './components/AshleyEditor';
import { renderEmojis } from './utils/emojis';

// expose some modules to the global window object
declare var window: any;
window.Ashley = {
  Editor: AshleyEditor,
};

document.addEventListener('DOMContentLoaded', event => {
  renderEmojis();
});

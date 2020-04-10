import * as AshleyEditor from './components/AshleyEditor';

// expose some modules to the global window object
declare var window: any;
window.Ashley = {
  Editor: AshleyEditor,
};

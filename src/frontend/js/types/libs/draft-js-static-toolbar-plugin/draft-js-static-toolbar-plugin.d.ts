declare module 'draft-js-static-toolbar-plugin' {
  function createToolbarPlugin(config?: any): PluginEditor;

  export const Separator: ComponentType<any>;

  export = createToolbarPlugin;
}

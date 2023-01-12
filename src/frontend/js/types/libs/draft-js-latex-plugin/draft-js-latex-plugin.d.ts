declare module 'draft-js-latex-plugin' {
  import { DraftHandleValue, EditorState } from 'draft-js';
  export function getLaTeXPlugin(
    config?: object,
  ): {
    initialize: (editorStore: object) => void;
    decorators: any[];
    blockRendererFn: (block: any) => any;
    handleKeyCommand: (
      command: string,
      editorState: EditorState,
      timestamp: number,
      store: object,
    ) => DraftHandleValue.HANDLED | DraftHandleValue.NOT_HANDLED;
    keyBindingFn: (e: any) => any;
  };
}
declare module 'draft-js-latex-plugin/lib/utils/insertTeX' {
  export function insertInlineTeX(editorState: EditorState): EditorState;
  export function insertTeXBlock(editorState: EditorState): EditorState;
}

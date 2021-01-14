declare module 'draft-js-code' {
  import { EditorState } from 'draft-js';

  function getKeyBinding(event: React.KeyboardEvent): string;
  function hasSelectionInBlock(editorState: EditorState): boolean;
  function handleKeyCommand(
    editorState: EditorState,
    command: string,
  ): EditorState;
  function handleReturn(
    event: React.KeyboardEvent,
    editorState: EditorState,
  ): EditorState;
  function onTab(
    event: React.KeyboardEvent,
    editorState: EditorState,
  ): EditorState;

  export = {
    getKeyBinding,
    hasSelectionInBlock,
    handleKeyCommand,
    handleReturn,
    onTab,
  };
}

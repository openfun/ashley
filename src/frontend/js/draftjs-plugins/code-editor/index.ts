/**
 * Credits :
 * Forked from https://github.com/withspectrum/draft-js-code-editor-plugin
 * - added an unstyle block after key return is pressed. This is done by inserting a new
 *   block when the split-block keyCommand is fired.
 */

import CodeUtils from 'draft-js-code';
import Draft, {
  ContentBlock,
  EditorState,
  KeyBindingUtil,
  RichUtils,
  DraftEditorCommand,
} from 'draft-js';
import { EditorPlugin, PluginFunctions } from '@draft-js-plugins/editor/lib';
import React from 'react';
import { List } from 'immutable';

const createCodeEditorPlugin = (): EditorPlugin => {
  return {
    handleKeyCommand(
      command: string,
      editorState: EditorState,
      eventTimeStamp: number,
      { setEditorState }: PluginFunctions,
    ) {
      const newState = CodeUtils.hasSelectionInBlock(editorState)
        ? CodeUtils.handleKeyCommand(editorState, command)
        : RichUtils.handleKeyCommand(editorState, command);

      if (newState) {
        setEditorState(newState);
        return 'handled';
      }
      return 'not-handled';
    },
    keyBindingFn(
      evt: React.KeyboardEvent,
      { getEditorState }: PluginFunctions,
    ) {
      return !CodeUtils.hasSelectionInBlock(getEditorState())
        ? Draft.getDefaultKeyBinding(evt)
        : (CodeUtils.getKeyBinding(evt) as DraftEditorCommand);
    },
    handleReturn(
      evt: React.KeyboardEvent,
      editorState: EditorState,
      { setEditorState }: PluginFunctions,
    ) {
      if (!CodeUtils.hasSelectionInBlock(editorState)) return 'not-handled';
      const selection = editorState.getSelection();
      // Add an unstyle block after key return is pressed. Detect when the keyCommand is fired and split the block
      if (selection.isCollapsed() && KeyBindingUtil.hasCommandModifier(evt)) {
        const contentState = editorState.getCurrentContent();
        const newBlock = new ContentBlock({
          key: Draft.genKey(),
          type: 'unstyled',
          text: '',
          characterList: List(),
        });
        const newBlockMap = contentState
          .getBlockMap()
          .set(newBlock.getKey(), newBlock);
        const newState = Draft.EditorState.push(
          editorState,
          Draft.ContentState.createFromBlockArray(newBlockMap.toArray()).set(
            'selectionAfter',
            contentState.getSelectionAfter().merge({
              anchorKey: newBlock.getKey(),
              anchorOffset: 0,
              focusKey: newBlock.getKey(),
              focusOffset: 0,
              isBackward: false,
            }),
          ) as Draft.ContentState,
          'split-block',
        );
        setEditorState(newState);
        return 'handled';
      }
      setEditorState(CodeUtils.handleReturn(evt, editorState));
      return 'handled';
    },
    onTab(
      evt: React.KeyboardEvent,
      { getEditorState, setEditorState }: PluginFunctions,
    ) {
      const editorState = getEditorState();
      if (!CodeUtils.hasSelectionInBlock(editorState)) return;

      setEditorState(CodeUtils.onTab(evt, editorState));
      return true;
    },
  };
};

export default createCodeEditorPlugin;

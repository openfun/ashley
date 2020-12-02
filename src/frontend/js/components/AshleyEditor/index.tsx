import { convertFromRaw, convertToRaw, EditorState, RichUtils } from 'draft-js';
import createLinkPlugin from 'draft-js-anchor-plugin';
import {
  BoldButton,
  HeadlineOneButton,
  HeadlineThreeButton,
  HeadlineTwoButton,
  ItalicButton,
  OrderedListButton,
  UnderlineButton,
  UnorderedListButton,
} from 'draft-js-buttons';
import createEmojiPlugin, { EmojiPluginConfig } from 'draft-js-emoji-plugin';
import Editor from 'draft-js-plugins-editor';
import PluginEditor from 'draft-js-plugins-editor/lib';
import createToolbarPlugin, { Separator } from 'draft-js-static-toolbar-plugin';
import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';

interface MyEditorProps {
  autofocus?: boolean;
  placeholder?: string;
  target: HTMLInputElement;
  emojiConfig?: EmojiPluginConfig;
  linkPlaceholder?: string;
}

const AshleyEditor = (props: MyEditorProps) => {
  const [editorState, setEditorState] = useState(() => {
    if (props.target.value) {
      const jsonContent = JSON.parse(props.target.value);
      if (jsonContent) {
        return EditorState.createWithContent(convertFromRaw(jsonContent));
      }
    }
    return EditorState.createEmpty();
  });

  const editorRef = useRef(null as PluginEditor | null);

  // Instantiate plugins in a state to avoid instantiation on every render
  const [{ emojiPlugin, linkPlugin, toolbarPlugin }] = useState(() => {
    return {
      emojiPlugin: createEmojiPlugin(props.emojiConfig),
      linkPlugin: createLinkPlugin({
        linkTarget: '_blank',
        placeholder: props.linkPlaceholder,
        theme: {
          input: 'ashley-editor-link-input',
          inputInvalid: 'ashley-editor-link-input-invalid',
          link: 'ashley-editor-link',
        },
      }),
      toolbarPlugin: createToolbarPlugin(),
    };
  });

  useEffect(() => {
    if (props.autofocus) {
      focusEditor();
    }
  }, []);

  const editorChange = (stateEditor: EditorState) => {
    props.target.value = JSON.stringify(
      convertToRaw(stateEditor.getCurrentContent()),
    );
    setEditorState(stateEditor);
  };

  const focusEditor = () => {
    if (editorRef.current != null) {
      editorRef.current.focus();
    }
  };

  const keyBinding = (command: string, stateEditor: EditorState) => {
    const newState = RichUtils.handleKeyCommand(stateEditor, command);
    if (newState) {
      editorChange(newState);
      return 'handled';
    }
    return 'not-handled';
  };

  return (
    <div className="ashley-editor-wrapper">
      <div className="ashley-editor-widget" onClick={focusEditor}>
        <Editor
          ref={editorRef}
          editorState={editorState}
          onChange={editorChange}
          plugins={[toolbarPlugin, emojiPlugin, linkPlugin]}
          placeholder={props.placeholder}
          handleKeyCommand={keyBinding}
        />
        <emojiPlugin.EmojiSuggestions />
      </div>
      <div className="ashley-editor-toolbar">
        <toolbarPlugin.Toolbar>
          {(externalProps: any) => (
            <div className="ashley-editor-buttons">
              <BoldButton {...externalProps} />
              <ItalicButton {...externalProps} />
              <UnderlineButton {...externalProps} />
              <linkPlugin.LinkButton {...externalProps} />
              <Separator {...externalProps} />
              <HeadlineOneButton {...externalProps} />
              <HeadlineTwoButton {...externalProps} />
              <HeadlineThreeButton {...externalProps} />
              <UnorderedListButton {...externalProps} />
              <OrderedListButton {...externalProps} />
              <emojiPlugin.EmojiSelect {...externalProps} />
            </div>
          )}
        </toolbarPlugin.Toolbar>
      </div>
    </div>
  );
};

export function init(props: MyEditorProps, container: HTMLElement) {
  ReactDOM.render(<AshleyEditor {...props} />, container);
}

import {
  convertFromRaw,
  convertToRaw,
  EditorState,
  RichUtils,
  Modifier,
} from 'draft-js';
import createLinkPlugin from '@draft-js-plugins/anchor';
import Editor from '@draft-js-plugins/editor';
import PluginEditor from '@draft-js-plugins/editor/lib';
import createMentionPlugin, {
  defaultSuggestionsFilter,
  MentionData,
} from '@draft-js-plugins/mention';
import createToolbarPlugin, {
  Separator,
} from '@draft-js-plugins/static-toolbar';
import createEmojiPlugin, { EmojiPluginConfig } from 'draft-js-emoji-plugin';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import {
  BoldButton,
  HeadlineOneButton,
  HeadlineThreeButton,
  HeadlineTwoButton,
  ItalicButton,
  OrderedListButton,
  UnderlineButton,
  UnorderedListButton,
  BlockquoteButton,
  CodeBlockButton,
} from '@draft-js-plugins/buttons';
import createCodeEditorPlugin from '../../draftjs-plugins/code-editor';

interface MyEditorProps {
  autofocus?: boolean;
  placeholder?: string;
  target: HTMLInputElement;
  emojiConfig?: EmojiPluginConfig;
  linkPlaceholder?: string;
  mentions?: MentionData[];
}

export const AshleyEditor = (props: MyEditorProps) => {
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
  const [
    { emojiPlugin, linkPlugin, toolbarPlugin, codeEditorPlugin },
  ] = useState({
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
    codeEditorPlugin: createCodeEditorPlugin(),
  });

  useEffect(() => {
    if (props.autofocus) {
      focusEditor();
    }
  }, []);

  // On HandlePastedText modify the current block in order to not create a different block for each pasted line
  const handlePastedText = (
    pastedText: string,
    html: string | undefined,
    stateEditor: EditorState,
  ) => {
    const selection = stateEditor.getSelection();
    const contentState = stateEditor.getCurrentContent();
    const startKey = selection.getStartKey();
    const currentBlock = contentState.getBlockForKey(startKey);

    if (currentBlock.getType() === 'code-block') {
      const newContent = Modifier.replaceText(
        stateEditor.getCurrentContent(),
        stateEditor.getSelection(),
        pastedText,
      );
      editorChange(
        EditorState.push(stateEditor, newContent, 'insert-characters'),
      );
      return 'handled';
    }
    return 'not-handled';
  };

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

  const PluginRenderers = [<emojiPlugin.EmojiSuggestions key="emoji" />];
  const plugins = [toolbarPlugin, emojiPlugin, linkPlugin, codeEditorPlugin];

  if (props.mentions) {
    const [{ mentionPlugin }] = useState({
      mentionPlugin: createMentionPlugin(),
    });
    const [open, setOpen] = useState(true);
    const [suggestions, setSuggestions] = useState(props.mentions);
    const onSearchChange = useCallback(({ value }: { value: string }) => {
      setSuggestions(defaultSuggestionsFilter(value, props.mentions!));
    }, []);
    plugins.push(mentionPlugin);
    PluginRenderers.push(
      <mentionPlugin.MentionSuggestions
        key="mentions"
        open={open}
        onOpenChange={setOpen}
        suggestions={suggestions}
        onSearchChange={onSearchChange}
      />,
    );
  }

  return (
    <div className="ashley-editor-wrapper">
      <div className="ashley-editor-widget" onClick={focusEditor}>
        <Editor
          ref={editorRef}
          editorState={editorState}
          onChange={editorChange}
          plugins={plugins}
          placeholder={props.placeholder}
          handleKeyCommand={keyBinding}
          handlePastedText={handlePastedText}
        />
        {PluginRenderers.map((Plugin) => Plugin)}
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
              <BlockquoteButton {...externalProps} />
              <CodeBlockButton {...externalProps} />
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

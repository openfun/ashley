import {
  convertFromRaw,
  convertToRaw,
  EditorState,
  RichUtils,
  Modifier,
} from 'draft-js';
import createLinkPlugin from '@draft-js-plugins/anchor';

import Editor, { composeDecorators } from '@draft-js-plugins/editor';
import PluginEditor from '@draft-js-plugins/editor/lib';
import createMentionPlugin, {
  defaultSuggestionsFilter,
  MentionData,
} from '@draft-js-plugins/mention';
import createToolbarPlugin, {
  Separator,
} from '@draft-js-plugins/static-toolbar';
import createEmojiPlugin, { EmojiPluginConfig } from 'draft-js-emoji-plugin';
import createImagePlugin from '@draft-js-plugins/image';
import React, { useCallback, useEffect, useRef, useState } from 'react';
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
import { ImageAdd } from './ImageAdd';
import { LatexButton } from './LatexButton';
import createAlignmentPlugin from '@draft-js-plugins/alignment';
import createFocusPlugin from '@draft-js-plugins/focus';
import createResizeablePlugin from '@draft-js-plugins/resizeable';
import createBlockDndPlugin from '@draft-js-plugins/drag-n-drop';
import { useIntl } from 'react-intl';
import { messagesEditor } from './messages';
import { getLaTeXPlugin } from 'draft-js-latex-plugin';
import { TypeLatexStyle, DraftHandleValue } from '../../types/Enums';

interface MyEditorProps {
  autofocus?: boolean;
  target: string;
  emojiConfig?: EmojiPluginConfig;
  mentions?: MentionData[];
  forum: number;
}

export const AshleyEditor = (props: MyEditorProps) => {
  const [editorState, setEditorState] = useState(() => {
    const target = document.getElementById(props.target) as HTMLInputElement;
    if (target != null && target.value) {
      const jsonContent = JSON.parse(target.value);
      if (jsonContent) {
        return EditorState.createWithContent(convertFromRaw(jsonContent));
      }
    }
    return EditorState.createEmpty();
  });
  const editorRef = useRef(null as PluginEditor | null);
  const intl = useIntl();

  // Instantiate plugins in a state to avoid instantiation on every render
  const [
    {
      emojiPlugin,
      linkPlugin,
      toolbarPlugin,
      blockDndPlugin,
      alignmentPlugin,
      focusPlugin,
      resizeablePlugin,
    },
  ] = useState({
    emojiPlugin: createEmojiPlugin(props.emojiConfig),
    linkPlugin: createLinkPlugin({
      linkTarget: '_blank',
      placeholder: intl.formatMessage(messagesEditor.linkPlaceholderEditor),
      theme: {
        input: 'ashley-editor-link-input',
        inputInvalid: 'ashley-editor-link-input-invalid',
        link: 'ashley-editor-link',
      },
    }),
    toolbarPlugin: createToolbarPlugin(),
    blockDndPlugin: createBlockDndPlugin(),
    alignmentPlugin: createAlignmentPlugin(),
    focusPlugin: createFocusPlugin(),
    resizeablePlugin: createResizeablePlugin({
      vertical: 'relative',
      horizontal: 'relative',
    }),
  });

  const [{ decorator }] = useState({
    decorator: composeDecorators(
      resizeablePlugin.decorator,
      alignmentPlugin.decorator,
      focusPlugin.decorator,
      blockDndPlugin.decorator,
    ),
  });

  const [{ imagePlugin }] = useState({
    imagePlugin: createImagePlugin({ decorator }),
  });
  const [{ LaTeXPlugin }] = useState({
    LaTeXPlugin: getLaTeXPlugin({}),
  });
  const { AlignmentTool } = alignmentPlugin;

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
      return DraftHandleValue.HANDLED;
    }
    return DraftHandleValue.NOT_HANDLED;
  };

  const editorChange = (stateEditor: EditorState) => {
    const target = document.getElementById(props.target) as HTMLInputElement;
    target.value = JSON.stringify(
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
      return DraftHandleValue.HANDLED;
    }
    return DraftHandleValue.NOT_HANDLED;
  };

  const PluginRenderers = [<emojiPlugin.EmojiSuggestions key="emoji" />];
  const plugins = [
    toolbarPlugin,
    emojiPlugin,
    linkPlugin,
    blockDndPlugin,
    focusPlugin,
    alignmentPlugin,
    resizeablePlugin,
    imagePlugin,
    LaTeXPlugin,
  ];

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
          placeholder={intl.formatMessage(messagesEditor.placeholderEditor)}
          handleKeyCommand={keyBinding}
          handlePastedText={handlePastedText}
        />
        <AlignmentTool />
        {PluginRenderers.map((Plugin) => Plugin)}
      </div>
      <div className="ashley-editor-toolbar">
        <toolbarPlugin.Toolbar>
          {(externalProps: any) => (
            <div className="ashley-editor-buttons">
              <BoldButton {...externalProps} />
              <ItalicButton {...externalProps} />
              <UnderlineButton {...externalProps} />
              <ImageAdd
                editorState={editorState}
                onChange={editorChange}
                modifier={imagePlugin.addImage}
                forum={props.forum}
                {...externalProps}
              />
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
              <Separator {...externalProps} />
              <LatexButton
                editorState={editorState}
                {...externalProps}
                type={TypeLatexStyle.INLINE}
              />
              <LatexButton
                editorState={editorState}
                {...externalProps}
                type={TypeLatexStyle.BLOCK}
              />
              <Separator {...externalProps} />
            </div>
          )}
        </toolbarPlugin.Toolbar>
      </div>
    </div>
  );
};

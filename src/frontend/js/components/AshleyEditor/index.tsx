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
import createEmojiPlugin, {
  EmojiPlugin,
  EmojiPluginConfig,
} from 'draft-js-emoji-plugin';
import Editor from 'draft-js-plugins-editor';
import PluginEditor from 'draft-js-plugins-editor/lib';
import createToolbarPlugin, { Separator } from 'draft-js-static-toolbar-plugin';
import React, { ComponentType, Ref } from 'react';
import ReactDOM from 'react-dom';

interface MyEditorProps {
  autofocus?: boolean;
  placeholder?: string;
  target: HTMLInputElement;
  emojiConfig?: EmojiPluginConfig;
}

// Initialize the Toolbar plugin
const toolbarPlugin = createToolbarPlugin();
const { Toolbar } = toolbarPlugin;

// Initialize the link plugin
const linkPlugin = createLinkPlugin({
  linkTarget: '_blank',
});
const { LinkButton } = linkPlugin;

export class AshleyEditor extends React.Component<MyEditorProps, any> {
  private toolbarRef: HTMLDivElement | null;
  private editorRef: PluginEditor | null;

  private emojiPlugin: EmojiPlugin;

  constructor(props: MyEditorProps) {
    super(props);

    // Initialize the Emoji plugin
    this.emojiPlugin = createEmojiPlugin(props.emojiConfig);

    this.toolbarRef = null;
    this.editorRef = null;

    this.state = {
      editorState: this.initialEditorState(),
    };
  }

  onChange(editorState: EditorState) {
    this.setState({ editorState });
    const rawContent = convertToRaw(editorState.getCurrentContent());
    this.props.target.value = JSON.stringify(rawContent);
  }

  handleKeyCommand(command: string, editorState: EditorState) {
    const newState = RichUtils.handleKeyCommand(editorState, command);
    if (newState) {
      this.onChange(newState);
      return 'handled';
    }
    return 'not-handled';
  }

  componentDidMount() {
    if (this.props.autofocus) {
      this.editorRef?.focus();
    }

    // Fix to be able to render the toolbar before the editor
    // See: https://github.com/draft-js-plugins/draft-js-plugins/issues/1369
    if (this.toolbarRef) {
      this.toolbarRef.addEventListener('click', () => {
        setTimeout(() => {
          this.setState({
            editorState: EditorState.forceSelection(
              this.state.editorState,
              this.state.editorState.getSelection(),
            ),
          });
        }, 0);
      });
    }
  }

  render() {
    return (
      <div>
        <Toolbar>
          {(externalProps: any) => (
            <div
              ref={toolbar => (this.toolbarRef = toolbar)}
              className="ashley-editor-buttons"
            >
              <BoldButton {...externalProps} />
              <ItalicButton {...externalProps} />
              <UnderlineButton {...externalProps} />
              <Separator {...externalProps} />
              <HeadlineOneButton {...externalProps} />
              <HeadlineTwoButton {...externalProps} />
              <HeadlineThreeButton {...externalProps} />
              <UnorderedListButton {...externalProps} />
              <OrderedListButton {...externalProps} />
              <this.emojiPlugin.EmojiSelect {...externalProps} />
            </div>
          )}
        </Toolbar>
        <div className="ashley-editor-widget">
          <Editor
            editorState={this.state.editorState}
            onChange={e => this.onChange(e)}
            plugins={[toolbarPlugin, this.emojiPlugin, linkPlugin]}
            placeholder={this.props.placeholder}
            handleKeyCommand={this.handleKeyCommand}
            ref={element => {
              this.editorRef = element;
            }}
          />
        </div>
        <this.emojiPlugin.EmojiSuggestions />
      </div>
    );
  }

  private initialEditorState() {
    if (this.props.target.value) {
      const jsonContent = JSON.parse(this.props.target.value);
      if (jsonContent) {
        return EditorState.createWithContent(convertFromRaw(jsonContent));
      }
    }
    return EditorState.createEmpty();
  }
}

export function init(props: MyEditorProps, container: HTMLElement) {
  ReactDOM.render(<AshleyEditor {...props} />, container);
}

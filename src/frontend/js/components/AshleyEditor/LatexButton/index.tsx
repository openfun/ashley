import React, { useMemo, useEffect, useRef, useState } from 'react';
import { DraftJsButtonTheme } from '@draft-js-plugins/buttons';
import { EditorState } from 'draft-js';
import {
  insertInlineTeX,
  insertTeXBlock,
} from 'draft-js-latex-plugin/lib/utils/insertTeX';
import { FormattedMessage } from 'react-intl';
import Tooltip from 'rc-tooltip';
import { messagesEditor } from '../messages';
import { DraftHandleValue, TypeLatexStyle } from '../../../types/Enums';

interface LatexButtonProps {
  type: string;
  theme: DraftJsButtonTheme;
  editorState: EditorState;
  getEditorState: () => EditorState;
  setEditorState: (editorState: EditorState) => void;
}

export const LatexButton = (props: LatexButtonProps) => {
  const node = useRef<HTMLDivElement>(null);
  const { buttonWrapper = '', button, active } = props.theme;
  const [isActive, setIsActive] = useState(false);

  const isInlineTeXSelected = () => {
    const selection = props.editorState.getSelection();
    const contentState = props.editorState.getCurrentContent();
    const blockKey = selection.getStartKey();
    const block = contentState.getBlockForKey(blockKey);
    const offset = selection.getIsBackward()
      ? selection.getStartOffset()
      : selection.getEndOffset();
    const entityKey = block?.getEntityAt(offset);
    if (!entityKey) {
      return false;
    }
    return contentState.getEntity(entityKey).getType() === 'INLINETEX';
  };

  const isLatexBlock = () => {
    const selection = props.editorState.getSelection();
    const block = props.editorState
      .getCurrentContent()
      .getBlockForKey(selection.getStartKey());
    return block.getData().get('type') === 'TEXBLOCK';
  };

  useEffect(() => {
    if (props.type === TypeLatexStyle.BLOCK) {
      setIsActive(isLatexBlock());
    } else if (props.type === TypeLatexStyle.INLINE) {
      setIsActive(isInlineTeXSelected());
    }
  }, [props.editorState]);

  const imageClassName = useMemo(
    () => `latex-${props.type} ${button} ${isActive ? active : ''}`,
    [props.type, isActive],
  );

  const handleAddLatex = (
    e: React.MouseEvent<HTMLButtonElement>,
    type: string,
  ) => {
    e.preventDefault();
    let newEditorState;
    const editorState = props.getEditorState();
    if (type === TypeLatexStyle.BLOCK) {
      newEditorState = insertTeXBlock(editorState);
    } else {
      newEditorState = insertInlineTeX(editorState);
    }
    props.setEditorState(newEditorState);
    return DraftHandleValue.HANDLED;
  };
  return (
    <div className={buttonWrapper} ref={node}>
      <Tooltip
        overlay={
          <FormattedMessage
            {...(props.type === TypeLatexStyle.INLINE
              ? messagesEditor.toolTipAddLatexInline
              : messagesEditor.toolTipAddLatexBlock)}
          />
        }
        placement="bottom"
      >
        <button
          data-testid={`addLatex${props.type}`}
          className={`${imageClassName}`}
          onClick={(e) => handleAddLatex(e, props.type)}
          type="button"
        />
      </Tooltip>
    </div>
  );
};

import React from 'react';
import { render, fireEvent } from '@testing-library/react';
import { EditorState, ContentState } from 'draft-js';
import { IntlProvider } from 'react-intl';

import {
  insertInlineTeX,
  insertTeXBlock,
} from 'draft-js-latex-plugin/lib/utils/insertTeX';
import { TypeLatexStyle } from '../../../types/Enums';
import { LatexButton } from '.';

const editor = EditorState.createWithContent(
  ContentState.createFromText('Hello World!'),
);

const props = {
  editorState: editor,
  type: TypeLatexStyle.INLINE,
  getEditorState: jest.fn(),
  setEditorState: jest.fn(),
  theme: {
    button: '',
    buttonWrapper: '',
    active: 'active',
  },
};
jest.mock('draft-js-latex-plugin/lib/utils/insertTeX', () => ({
  insertInlineTeX: jest.fn(),
  insertTeXBlock: jest.fn(),
}));

describe('LatexButton', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });
  it('should handle adding inline latex', () => {
    const { getByTestId } = render(<LatexButton {...props} />);
    const button = getByTestId('addLatexinline');
    fireEvent.click(button);
    expect(props.setEditorState).toHaveBeenCalled();
    expect(props.getEditorState).toHaveBeenCalled();
    expect(insertInlineTeX).toHaveBeenCalled();
    expect(insertTeXBlock).not.toHaveBeenCalled();
  });

  it('shows the tooltip text over inline latex button is be present', () => {
    const { getByRole, getByTestId } = render(
      <IntlProvider locale="en">
        <LatexButton {...props} />
      </IntlProvider>,
    );
    const button = getByTestId('addLatexinline');
    fireEvent.mouseEnter(button);
    getByRole('tooltip', { name: 'Add a Latex inline mathematical formula' });
  });

  it('should handle adding block latex', () => {
    props.type = TypeLatexStyle.BLOCK;
    const { getByTestId } = render(<LatexButton {...props} />);
    const button = getByTestId('addLatexblock');
    fireEvent.click(button);
    expect(props.setEditorState).toHaveBeenCalled();
    expect(props.getEditorState).toHaveBeenCalled();
    expect(insertInlineTeX).not.toHaveBeenCalled();
    expect(insertTeXBlock).toHaveBeenCalled();
  });

  it('shows the tooltip text over latex block button is be present', () => {
    props.type = TypeLatexStyle.BLOCK;
    const { getByRole, getByTestId } = render(
      <IntlProvider locale="en">
        <LatexButton {...props} />
      </IntlProvider>,
    );
    const button = getByTestId('addLatexblock');
    fireEvent.mouseEnter(button);
    getByRole('tooltip', {
      name: 'Add a Latex mathematical formula in a new block',
    });
  });
});

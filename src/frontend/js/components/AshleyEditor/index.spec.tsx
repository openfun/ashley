import { render, screen } from '@testing-library/react';
import React from 'react';

import { AshleyEditor } from '.';

describe('AshleyEditor', () => {
  it('renders the editor and expected elements are present', () => {
    const target = document.createElement('input');
    const { container } = render(<AshleyEditor target={target} />);

    // check that module draftjs is loaded
    screen.getByRole('combobox');

    // check that the toolbar plugin has been added
    screen.getByRole('button', {
      name: /h1/i,
    });

    // check if emoticon has been added to the toolbar plugin editor
    screen.getByRole('button', {
      name: /☺/i,
    });

    // check if quotation has been added to the toolbar plugin editor
    const quotationButton = container.querySelector(
      'path[d="M6 17h3l2-4V7H5v6h3zm8 0h3l2-4V7h-6v6h3z"]',
    );
    expect(quotationButton).toBeInTheDocument();

    // check if link button has been added to the toolbar plugin editor
    const linkButton = container.querySelector(
      'path[d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"]',
    );
    expect(linkButton).toBeInTheDocument();
  });
});

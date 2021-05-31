import { createEvent } from '@testing-library/dom';
import { render, fireEvent, screen } from '@testing-library/react';
import user from '@testing-library/user-event';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { AshleyEditor } from '.';
import { BlockMapFactory } from '../../utils/test/factories';
/***
 *  useful ressources
    Draft.js's components does not change its content with keypress, keydown or change events
    ref https://spectrum.chat/testing-library/help/has-anyone-successfully-used-rtl-to-test[…]nts-on-a-draftjs-text-box~f1928053-9e53-407a-9be5-70babeb4b692
        https://github.com/facebook/draft-js/issues/743
 ***/
jest.mock('../../data/frontEndData', () => ({
  appFrontendContext: {
    csrftoken: 'foo',
    max_upload: 1,
    image_type: ['.gif', '.jpeg', '.jpg', '.png', '.svg'],
  },
}));

describe('AshleyEditor', () => {
  const props = {
    forum: 1,
  };
  afterEach(() => {
    jest.resetAllMocks();
  });

  // add input target, it's value is linked with editor content and needed for all the tests
  const target = document.createElement('input');
  target.setAttribute('id', 'target');
  document.body.append(target);

  it('renders the editor and expected elements are present', () => {
    const { container } = render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" {...props} />
      </IntlProvider>,
    );

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

    // check if code button has been added to the toolbar plugin editor
    const codeButton = container.querySelector(
      'path[d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"]',
    );
    expect(codeButton).toBeInTheDocument();

    // check if button to addImage has been added to the toolbar
    screen.getByTestId('addImage');
  });

  it('loads AshleyEditor component with existing json content containing a code-block and an unstyled block', () => {
    target.value = BlockMapFactory([
      {
        key: 'brt6g',
        text: 'ce texte est ajouté dans code-block.',
        type: 'code-block',
      },
      {
        inlineStyleRanges: [
          {
            offset: 0,
            length: 21,
            style: 'BOLD',
          },
        ],
        text: 'ce texte est en gras.',
        type: 'unstyled',
      },
    ]);

    const { container } = render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" {...props} />
      </IntlProvider>,
    );
    // check that the content is now present in the editor
    screen.getByText(/ce texte est ajouté dans code-block./i);
    screen.getByText(/ce texte est en gras./i);

    // validate that the block code-block is in the expected pre element with the expected draft-js class
    // we use a selector on purpose to confirm that draft-js has been loaded
    expect(
      container.querySelector(
        'pre.public-DraftStyleDefault-pre [data-text="true"]',
      ),
    ).toHaveTextContent('ce texte est ajouté dans code-block.');
  });

  it('updates the input loaded in AshleyEditor when we change the content of the editor', () => {
    const { container } = render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" {...props} />
      </IntlProvider>,
    );

    // select the draft-js editor
    const editorNode = container.querySelector('.public-DraftEditor-content')!;
    // paste text
    const toBePasted = {
      clipboardData: {
        types: ['text/plain'],
        getData: (type: string) => "Je suis dans l'éditeur !",
      },
    };
    fireEvent(editorNode, createEvent.paste(editorNode, toBePasted));

    // check that the text is now present
    screen.getByText(/je suis dans l'éditeur !/i);
    // control it has been added to the input.value
    expect(target.value).toContain("Je suis dans l'éditeur !");
  });

  /*****
   * draft-js default behaviour for code block is to create a new code block for each pasted line
   * we test that the rewrite of handlePastedText is properly handled
   */
  it('pastes in a code-block and stays in the same draft-js code-block', () => {
    target.value = BlockMapFactory([
      {
        key: 'brt6g',
        text: 'Je suis ajouté comme code block !',
        type: 'code-block',
      },
    ]);

    const { container } = render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" {...props} />
      </IntlProvider>,
    );

    // target the code block
    const editorNode = container.querySelector(
      'pre.public-DraftStyleDefault-pre [data-text="true"]',
    )!;
    const toBePasted = {
      clipboardData: {
        types: ['text/plain'],
        getData: (type: string) => '<?php $i=100;?>',
      },
    };
    fireEvent(editorNode, createEvent.paste(editorNode, toBePasted));
    // check that text has been added in the editor
    screen.getByText(/Je suis ajouté comme code block !<\?php \$i=100;\?>/i);
    // check that it has been properly added in current code-block content
    expect(target.value).toEqual(
      BlockMapFactory([
        {
          key: 'brt6g',
          text: 'Je suis ajouté comme code block !<?php $i=100;?>',
          type: 'code-block',
        },
      ]),
    );
  });

  it('renders the editor with a list of users to mention', () => {
    // load the editor with no list of users to mention
    render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" {...props} />
      </IntlProvider>,
    );

    // check that list box containing the list of active users is not present
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();

    // load the editor with a list of active users to mention
    const mentionUsers = [
      { name: 'Paul', link: 'profil/user/10' },
      { name: 'Joséphine', link: 'profil/user/2' },
    ];

    const { container } = render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" mentions={mentionUsers} {...props} />
      </IntlProvider>,
    );

    // check that list box exists
    expect(screen.getByRole('listbox')).toBeInTheDocument();
    // check list contains the two users
    expect(screen.getAllByRole('option')).toHaveLength(2);
    screen.getByRole('option', { name: /joséphine/i });
    screen.getByRole('option', { name: /paul/i });
  });

  it('renders the editor with a pop up to add Image', () => {
    render(
      <IntlProvider locale="en">
        <AshleyEditor target="target" {...props} />
      </IntlProvider>,
    );
    const addToolbarButton = screen.getByTestId('addImage');
    expect(addToolbarButton.classList[0]).not.toContain(
      'add-image-pressed-button',
    );
    fireEvent.click(addToolbarButton);

    // pop up is now open
    expect(addToolbarButton.classList[0]).toContain('add-image-pressed-button');
    screen.getByText('Add image');
    screen.getByLabelText('Add image');

    const file = new File(['image'], 'image.png', { type: 'image/png' });
    Object.defineProperty(file, 'size', { value: 1024 * 1024 * 10 });

    const input = screen.getByLabelText('Add image') as HTMLInputElement;
    user.upload(input, file);
    expect(input.files![0]).toStrictEqual(file);

    screen.getByText(
      'An error occured uploading the image, the size of the file is over 1MB.',
    );
    // pop up is still open
    expect(addToolbarButton.classList[0]).toContain('add-image-pressed-button');

    // click on another button, make sure it closes the modal
    fireEvent.click(
      screen.getByRole('button', {
        name: /h1/i,
      }),
    );
    // pop up is now closed
    expect(addToolbarButton.classList[0]).not.toContain(
      'add-image-pressed-button',
    );
  });
});

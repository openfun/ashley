import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { Actions } from '../../../types/Enums';
import { Modal } from '.';

jest.mock('../../../data/frontEndData', () => ({
  appFrontendContext: { csrftoken: 'foo' },
  image_type: ['.gif', '.jpeg', '.jpg', '.png', '.svg'],
}));
const mocksetModalIsOpen = jest.fn();
const myProps = {
  user: {
    public_username: 'Thérèse',
    id: 8,
    roles: ['lambda_group', 'student', 'moderator'],
  },
  action: Actions.REVOKE,
  appElement: '#modal-exclude__react',
  modalIsOpen: true,
  setModalIsOpen: mocksetModalIsOpen,
  onChange: jest.fn(),
};

describe('<Modal />', () => {
  // create the element for the setAppElement used in the Modal
  const appContainer = document.createElement('div');
  appContainer.setAttribute('id', 'modal-exclude__react');
  document.body.append(appContainer);

  afterEach(() => {
    jest.resetAllMocks();
    fetchMock.reset();
  });

  it('renders modal buttons and text with the expected element', () => {
    render(
      <IntlProvider locale="en">
        <Modal {...myProps} />
      </IntlProvider>,
    );
    screen.getByRole('heading', { name: 'Revoke Thérèse to moderator' });
    screen.getByText('Are you certain you want to confirm this action ?');
    screen.getByRole('button', { name: 'Revoke moderator' });

    expect(screen.getAllByRole('button', { name: 'Close' })).toHaveLength(2);
  });

  it('fires SetModalIsOpen to false on closed button', () => {
    render(
      <IntlProvider locale="en">
        <Modal {...myProps} />
      </IntlProvider>,
    );
    const closedButton = screen.getAllByRole('button', { name: 'Close' })[0];
    fireEvent.click(closedButton);
    expect(mocksetModalIsOpen).toHaveBeenCalledWith(false);
    // canceled the action so nothing will change
    expect(myProps.onChange).not.toHaveBeenCalled();
  });

  it('modifies text depending on action', () => {
    render(
      <IntlProvider locale="en">
        <Modal {...{ ...myProps, action: Actions.PROMOTE }} />
      </IntlProvider>,
    );
    screen.getByRole('heading', { name: 'Promote Thérèse to moderator' });
    screen.getByRole('button', { name: 'Promote moderator' });
  });

  it('calls props.onChange and revoke on click button', async () => {
    fetchMock.mock(
      '/api/v1.0/users/8/',
      { status: 200, body: {} },
      { method: 'PUT' },
    );
    render(
      <IntlProvider locale="en">
        <Modal {...myProps} />
      </IntlProvider>,
    );

    const revokeButton = screen.getByRole('button', {
      name: 'Revoke moderator',
    });
    fireEvent.click(revokeButton);
    await waitFor(() => {
      expect(fetchMock.called('/api/v1.0/users/8/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1.0/users/8/')!.body).toEqual(
      '{"public_username":"Thérèse","id":8,"roles":["lambda_group","student"]}',
    );
    expect(myProps.onChange).toHaveBeenCalled();
  });

  it('calls props.onChange and promote on click button', async () => {
    fetchMock.mock(
      '/api/v1.0/users/8/',
      { status: 200, body: {} },
      { method: 'PUT' },
    );
    render(
      <IntlProvider locale="en">
        <Modal
          {...{
            ...myProps,
            action: Actions.PROMOTE,
            user: { ...myProps.user, roles: ['lambda_group', 'student'] },
          }}
        />
      </IntlProvider>,
    );

    const revokeButton = screen.getByRole('button', {
      name: 'Promote moderator',
    });
    fireEvent.click(revokeButton);
    await waitFor(() => {
      expect(fetchMock.called('/api/v1.0/users/8/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1.0/users/8/')!.body).toEqual(
      '{"public_username":"Thérèse","id":8,"roles":["lambda_group","student","moderator"]}',
    );
    expect(myProps.onChange).toHaveBeenCalled();
  });
});

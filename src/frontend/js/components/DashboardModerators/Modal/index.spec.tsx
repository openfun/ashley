import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import fetchMock from 'fetch-mock';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { Actions, Role } from '../../../types/Enums';
import { Modal } from '.';

jest.mock('../../../data/frontEndData', () => ({
  appFrontendContext: { csrftoken: 'foo' },
}));

fetchMock.mock('/api/v1/users/8/', {});

const myProps = {
  user: { public_username: 'Thérèse', id: 8, role: Role.MODERATOR },
  action: Actions.REVOKE,
  appElement: '#modal-exclude__react',
  modalIsOpen: true,
  setModalIsOpen: (value: boolean) => {
    console.warn(`SetModalIsOpen is called and value passed is ${value}`);
  },
  onChange: jest.fn(),
};

describe('<Modal />', () => {
  // create the element for the setAppElement used in the Modal
  const appContainer = document.createElement('div');
  appContainer.setAttribute('id', 'modal-exclude__react');
  document.body.append(appContainer);

  beforeEach(() => {
    jest.spyOn(console, 'warn').mockImplementation(() => {});
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
    expect(console.warn).toHaveBeenCalledWith(
      'SetModalIsOpen is called and value passed is false',
    );
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
      expect(fetchMock.called('/api/v1/users/8/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1/users/8/')!.body).toEqual(
      '{"public_username":"Thérèse","id":8,"role":"student"}',
    );
    expect(myProps.onChange).toHaveBeenCalled();
    // modals gets closed
    expect(console.warn).toHaveBeenCalledWith(
      'SetModalIsOpen is called and value passed is false',
    );
  });

  it('calls revoke update + props.onChange on click button', async () => {
    render(
      <IntlProvider locale="en">
        <Modal {...{ ...myProps, action: Actions.PROMOTE }} />
      </IntlProvider>,
    );

    const revokeButton = screen.getByRole('button', {
      name: 'Promote moderator',
    });
    fireEvent.click(revokeButton);
    await waitFor(() => {
      expect(fetchMock.called('/api/v1/users/8/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1/users/8/')!.body).toEqual(
      '{"public_username":"Thérèse","id":8,"role":"moderator"}',
    );
    expect(myProps.onChange).toHaveBeenCalled();
    // modals gets closed
    expect(console.warn).toHaveBeenCalledWith(
      'SetModalIsOpen is called and value passed is false',
    );
  });
});

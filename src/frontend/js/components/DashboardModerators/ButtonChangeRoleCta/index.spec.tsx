import fetchMock from 'fetch-mock';
import { waitFor, fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { Actions, Role } from '../../../types/Enums';
import { ButtonChangeRoleCta } from '.';

const props = {
  user: {
    public_username: 'Samuel',
    id: 2,
    role: Role.STUDENT,
  },
  action: Actions.PROMOTE,
  onChange: () => {
    console.warn('OnChange has been called for sure!');
  },
};
jest.mock('../../../data/frontEndData', () => ({
  appFrontendContext: { csrftoken: 'foo' },
}));
fetchMock.mock('/api/v1/users/2/', {});

describe('<ButtonChangeRoleCta />', () => {
  beforeEach(() => {
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  it('renders a button with proper action text depending on props param and calls onChange prop', async () => {
    render(
      <IntlProvider locale="en">
        <ButtonChangeRoleCta {...props} />
      </IntlProvider>,
    );
    const button = screen.getByRole('button', {
      name: 'Promote moderator',
    });

    fireEvent.click(button);
    await waitFor(() => {
      expect(fetchMock.called('/api/v1/users/2/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1/users/2/')!.body).toEqual(
      '{"public_username":"Samuel","id":2,"role":"moderator"}',
    );
    expect(console.warn).toHaveBeenCalledWith(
      'OnChange has been called for sure!',
    );
  });

  it('renders a button with proper action text depending on props param and calls onChange prop', async () => {
    render(
      <IntlProvider locale="en">
        <ButtonChangeRoleCta {...{ ...props, action: Actions.REVOKE }} />
      </IntlProvider>,
    );
    const button = screen.getByRole('button', {
      name: 'Revoke moderator',
    });

    fireEvent.click(button);
    await waitFor(() => {
      expect(fetchMock.called('/api/v1/users/2/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1/users/2/')!.body).toEqual(
      '{"public_username":"Samuel","id":2,"role":"student"}',
    );
    expect(console.warn).toHaveBeenCalledWith(
      'OnChange has been called for sure!',
    );
  });
});

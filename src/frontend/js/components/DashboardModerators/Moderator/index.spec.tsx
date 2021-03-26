import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { User } from '../../../types/User';
import { Role } from '../../../types/Enums';
import { Moderator } from '.';
const props = {
  user: {
    public_username: 'Samuel',
    id: 2,
    role: Role.MODERATOR,
  },
  onClick: (user: User) => {
    console.warn(
      `onClick ${user.public_username} with id ${user.id} has been called for sure!`,
    );
  },
};

describe('<Moderator />', () => {
  beforeEach(() => {
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(jest.restoreAllMocks);

  it('renders a button with expected text and calls onClick passed through props', async () => {
    render(
      <IntlProvider locale="en">
        <Moderator {...props} />
      </IntlProvider>,
    );
    const button = screen.getByRole('button', {
      name: 'Revoke moderator',
    });
    screen.getByText('Samuel');
    screen.getByRole('link', { name: 'Revoke moderator' });

    fireEvent.click(button);
    expect(console.warn).toHaveBeenCalledWith(
      'onClick Samuel with id 2 has been called for sure!',
    );
  });
});

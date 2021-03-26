import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { User } from '../../../types/User';
import { ListModerators } from '.';

const myProps = {
  users: [
    { public_username: 'Thérèse', id: 1, role: 'moderator' },
    { public_username: 'Thomas', id: 2, role: 'moderator' },
    { public_username: 'Sam', id: 3, role: 'moderator' },
  ],
  totalUsers: 5,
  setUser: (user: User) => {
    console.warn(
      `setUser has been called for user ${user.id} ${user.public_username}`,
    );
  },
  onChange: () => {
    console.warn('OnChange has been called for sure!');
  },
};

describe('<ListModerators />', () => {
  beforeEach(() => {
    render(
      <IntlProvider locale="en">
        <ListModerators {...myProps} />
      </IntlProvider>,
    );
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  it('renders the expected amount of mocked moderator components and handlers get called', () => {
    screen.getByText('3 moderators found from 5 users found');

    // Users from props are listed
    screen.getByText('Thérèse');
    screen.getByText('Thomas');
    screen.getByText('Sam');

    // We have 3 links and 3 buttons as expected
    expect(
      screen.getAllByRole('button', { name: 'Revoke moderator' }),
    ).toHaveLength(3);
    expect(
      screen.getAllByRole('link', { name: 'Revoke moderator' }),
    ).toHaveLength(3);

    // click on second button
    const button = screen.getAllByRole('button', {
      name: 'Revoke moderator',
    })[1];
    fireEvent.click(button);

    // handlers get called
    // the right user is targeted
    expect(console.warn).toHaveBeenCalledWith(
      'setUser has been called for user 2 Thomas',
    );
    expect(console.warn).toHaveBeenCalledWith(
      'OnChange has been called for sure!',
    );
  });

  it('renders text presenting the list with the expected numbers', () => {
    // default rendering for three users
    screen.getByText('3 moderators found from 5 users found');

    // rerender for one user to test the change to 1 user and sentence in singular
    render(
      <IntlProvider locale="en">
        <ListModerators
          {...{
            ...myProps,
            users: [{ public_username: '', id: 3, role: 'moderator' }],
          }}
        />
      </IntlProvider>,
    );

    screen.getByText('1 moderator found from 5 users found');
  });
});

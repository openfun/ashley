import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { ListModerators } from '.';

const mockSetUser = jest.fn();
const myProps = {
  users: [
    { public_username: 'Thérèse', id: 1 },
    { public_username: 'Thomas', id: 2 },
    { public_username: 'Sam', id: 3 },
  ],
  totalUsers: 5,
  setUser: mockSetUser,
  onChange: jest.fn(),
};

describe('<ListModerators />', () => {
  afterEach(jest.resetAllMocks);

  it('renders the expected amount of mocked moderator components and handlers get called', () => {
    render(
      <IntlProvider locale="en">
        <ListModerators {...myProps} />
      </IntlProvider>,
    );

    screen.getByText('3 moderators found from 5 users found');

    // Users from props are listed
    screen.getByText('Thérèse');
    screen.getByText('Thomas');
    screen.getByText('Sam');

    // We have 3 links and 3 buttons as expected
    expect(
      screen.getAllByRole('button', { name: 'Revoke moderator' }),
    ).toHaveLength(3);
    screen.getAllByRole('link', { name: "Access Thérèse's profil" });
    screen.getAllByRole('link', { name: "Access Thomas's profil" });
    screen.getAllByRole('link', { name: "Access Sam's profil" });

    // click on second button
    const button = screen.getAllByRole('button', {
      name: 'Revoke moderator',
    })[1];
    fireEvent.click(button);

    // handlers get called
    // the right user is targeted
    expect(mockSetUser).toHaveBeenCalledWith({
      public_username: 'Thomas',
      id: 2,
    });
    expect(myProps.onChange).toHaveBeenCalled();
  });

  it('renders text presenting the list with the expected numbers', () => {
    const { rerender } = render(
      <IntlProvider locale="en">
        <ListModerators {...myProps} />
      </IntlProvider>,
    );

    // default rendering for three users
    screen.getByText('3 moderators found from 5 users found');

    // rerender for one user to test the change to 1 user and sentence in singular
    rerender(
      <IntlProvider locale="en">
        <ListModerators
          {...{
            ...myProps,
            users: [{ public_username: '', id: 3 }],
          }}
        />
      </IntlProvider>,
    );

    screen.getByText('1 moderator found from 5 users found');
  });
});

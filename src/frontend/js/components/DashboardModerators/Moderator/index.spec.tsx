import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { Moderator } from '.';

const mockOnClick = jest.fn();

const props = {
  user: {
    public_username: 'Samuel',
    id: 2,
    roles: ['moderator'],
  },
  onClick: mockOnClick,
};

describe('<Moderator />', () => {
  afterEach(jest.resetAllMocks);

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
    screen.getByRole('button', { name: 'Revoke moderator' });
    screen.getByRole('link', { name: "Access Samuel's profil" });

    fireEvent.click(button);
    expect(mockOnClick).toHaveBeenCalledWith({
      public_username: 'Samuel',
      id: 2,
      roles: ['moderator'],
    });
  });
});

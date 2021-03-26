import { fireEvent, waitFor, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { User } from '../../../types/User';
import { Role } from '../../../types/Enums';
import { SelectStudentsSuggestField } from '.';

const myProps = {
  users: [
    { public_username: 'Thérèse', id: 1, role: Role.STUDENT },
    { public_username: 'thomas', id: 2, role: Role.STUDENT },
    { public_username: 'Valérie', id: 3, role: Role.STUDENT },
    { public_username: 'Zao', id: 4, role: Role.STUDENT },
    { public_username: 'Thibaut', id: 5, role: Role.STUDENT },
    { public_username: 'Noémie', id: 6, role: Role.STUDENT },
    { public_username: 'Zackari', id: 7, role: Role.STUDENT },
    { public_username: 'Zoé', id: 8, role: Role.STUDENT },
  ],
  setUser: (user: User) => {
    console.warn(
      `setUser has been called for user ${user.id} ${user.public_username}`,
    );
  },
  onChange: jest.fn(),
};

describe('<SelectStudentsSuggestField />', () => {
  beforeEach(() => {
    render(
      <IntlProvider locale="en">
        <SelectStudentsSuggestField {...myProps} />
      </IntlProvider>,
    );
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  it('renders suggestion on letter pressed with maximum 5 suggestions and in alphabetic order', async () => {
    screen.getByText('Add new moderator to the forum : 8 students found');
    const searchField = screen.getByPlaceholderText('Search for students');

    fireEvent.focus(searchField);

    // As soon as a key is pressed, list with maximum 5 is shown
    // no filter active as no username starts with letter ’a’
    fireEvent.change(searchField, { target: { value: 'a' } });
    await waitFor(() => {
      screen.getAllByRole('option');
    });
    expect(screen.getAllByRole('option')).toHaveLength(5);
    // list is rendered in alphabetic order
    expect(screen.getAllByRole('option')[0].firstChild).toHaveTextContent(
      'Noémie',
    );
    expect(screen.getAllByRole('option')[1].firstChild).toHaveTextContent(
      'Thérèse',
    );
    expect(screen.getAllByRole('option')[2].firstChild).toHaveTextContent(
      'Thibaut',
    );
    expect(screen.getAllByRole('option')[3].firstChild).toHaveTextContent(
      'thomas',
    );
    expect(screen.getAllByRole('option')[4].firstChild).toHaveTextContent(
      'Valérie',
    );
  });
  it('renders suggestion filtered with the first letter', async () => {
    const searchField = screen.getByPlaceholderText('Search for students');
    fireEvent.focus(searchField);

    // Press letter in minuscule, filters all the users that starts with n or N
    fireEvent.change(searchField, { target: { value: 'n' } });
    await waitFor(() => {
      screen.getAllByRole('option');
    });
    expect(screen.getAllByRole('option')).toHaveLength(1);
    expect(screen.getAllByRole('option')[0].firstChild).toHaveTextContent(
      'Noémie',
    );

    // Filters all the users that are starting with th or Th
    fireEvent.change(searchField, { target: { value: 'Th' } });
    await waitFor(() => {
      screen.getAllByRole('option');
    });
    expect(screen.getAllByRole('option')).toHaveLength(3);
    expect(screen.getAllByRole('option')[0].firstChild).toHaveTextContent(
      'Thérèse',
    );
    expect(screen.getAllByRole('option')[1].firstChild).toHaveTextContent(
      'Thibaut',
    );
    expect(screen.getAllByRole('option')[2].firstChild).toHaveTextContent(
      'thomas',
    );
  });

  it('calls onChange and update on selecting user ', async () => {
    const searchField = screen.getByPlaceholderText('Search for students');
    fireEvent.focus(searchField);

    // Press letter in minuscule filters whole the users that starts with n or N
    fireEvent.change(searchField, { target: { value: 'n' } });
    const selectedUser = screen.getByRole('option', { name: 'Noémie' });
    fireEvent.click(selectedUser);
    await waitFor(() => {
      expect(myProps.onChange).toHaveBeenCalledTimes(1);
    });
    expect(console.warn).toHaveBeenCalledWith(
      'setUser has been called for user 6 Noémie',
    );
  });
});

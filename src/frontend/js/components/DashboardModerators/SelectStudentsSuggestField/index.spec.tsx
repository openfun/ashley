import { fireEvent, waitFor, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { SelectStudentsSuggestField } from '.';

const mockSetUser = jest.fn();
const myProps = {
  users: [
    { public_username: 'Thérèse', id: 1 },
    { public_username: 'thomas', id: 2 },
    { public_username: 'Valérie', id: 3 },
    { public_username: 'Zao', id: 4 },
    { public_username: 'Thibaut', id: 5 },
    { public_username: 'Noémie', id: 6 },
    { public_username: 'Zackari', id: 7 },
    { public_username: 'Zoé', id: 8 },
  ],
  setUser: mockSetUser,
  onChange: jest.fn(),
};

describe('<SelectStudentsSuggestField />', () => {
  afterEach(jest.resetAllMocks);
  it('renders suggestion on letter pressed with maximum 5 suggestions and in alphabetic order', async () => {
    render(
      <IntlProvider locale="en">
        <SelectStudentsSuggestField {...myProps} />
      </IntlProvider>,
    );
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
    render(
      <IntlProvider locale="en">
        <SelectStudentsSuggestField {...myProps} />
      </IntlProvider>,
    );
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
    render(
      <IntlProvider locale="en">
        <SelectStudentsSuggestField {...myProps} />
      </IntlProvider>,
    );
    const searchField = screen.getByPlaceholderText('Search for students');
    fireEvent.focus(searchField);

    // Press letter in minuscule filters whole the users that starts with n or N
    fireEvent.change(searchField, { target: { value: 'n' } });
    const selectedUser = screen.getByRole('option', { name: 'Noémie' });
    fireEvent.click(selectedUser);
    await waitFor(() => {
      expect(myProps.onChange).toHaveBeenCalledTimes(1);
    });
    expect(mockSetUser).toHaveBeenCalledWith({
      public_username: 'Noémie',
      id: 6,
    });
  });
});

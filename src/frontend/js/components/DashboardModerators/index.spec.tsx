import fetchMock from 'fetch-mock';

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { Role } from '../../types/Enums';
import { DashboardModerators } from '.';

jest.mock('../../data/frontEndData', () => ({
  appFrontendContext: { csrftoken: 'foo' },
}));

describe('<DashboardModerators />', () => {
  fetchMock.get('/api/v1/users/?role=moderator', [
    { public_username: 'Samy', id: 9, role: Role.MODERATOR },
  ]);
  fetchMock.get('/api/v1/users/?role=student', [
    { public_username: 'Thérèse', id: 1, role: Role.STUDENT },
    { public_username: 'thomas', id: 2, role: Role.STUDENT },
    { public_username: 'Valérie', id: 3, role: Role.STUDENT },
    { public_username: 'Zao', id: 4, role: Role.STUDENT },
    { public_username: 'Thibaut', id: 5, role: Role.STUDENT },
    { public_username: 'Noémie', id: 6, role: Role.STUDENT },
    { public_username: 'Zackari', id: 7, role: Role.STUDENT },
    { public_username: 'Zoé', id: 8, role: Role.STUDENT },
  ]);
  fetchMock.mock('/api/v1/users/6/', {});
  // create the element for the setAppElement used in the Modal
  const appContainer = document.createElement('div');
  appContainer.setAttribute('id', 'modal-exclude__react');
  document.body.append(appContainer);

  it('renders the SelectStudentsSuggestField component called in this component', async () => {
    render(
      <IntlProvider locale="en">
        <DashboardModerators />
      </IntlProvider>,
    );

    // SelectStudentsSuggestField component is loaded
    await screen.findByPlaceholderText('Search for students');
    await screen.findByText(
      'Add new moderator to the forum : 8 students found',
    );
  });
  it('renders the ListModerators component called in this component', async () => {
    render(
      <IntlProvider locale="en">
        <DashboardModerators />
      </IntlProvider>,
    );

    // ListModerators component is loaded
    await screen.findByText('1 moderator found from 9 users found');
    await screen.findByRole('button', {
      name: /revoke moderator/i,
    });
  });
  it('renders the Modal component called in this component and Modal is functionnal from ListModerator', async () => {
    render(
      <IntlProvider locale="en">
        <DashboardModerators />
      </IntlProvider>,
    );

    const button = await screen.findByRole('button', {
      name: /revoke moderator/i,
    });
    // Modal component is loaded and operational from ListModerator
    fireEvent.click(button);
    await screen.findByRole('heading', { name: 'Revoke Samy to moderator' });
    await screen.findByText(
      'Are you certain you want to confirm this action ?',
    );
    const closed = await screen.findAllByRole('button', { name: 'Close' });
    fireEvent.click(closed[0]);
    // Modal is now closed
    expect(screen.queryByRole('button', { name: 'Close' })).toBeNull();
    expect(
      screen.queryByRole('heading', { name: 'Revoke Samy to moderator' }),
    ).toBeNull();
  });
  it('renders the Modal from selecting a user and on validation list gets updated', async () => {
    render(
      <IntlProvider locale="en">
        <DashboardModerators />
      </IntlProvider>,
    );
    // Modal component is loaded and operational from SelectStudentsSuggestField
    const selectStudent = await screen.findByPlaceholderText(
      'Search for students',
    );
    fireEvent.focus(selectStudent);
    fireEvent.change(selectStudent, { target: { value: 'n' } });
    const selectedUser = await screen.findByRole('option', { name: 'Noémie' });
    fireEvent.click(selectedUser);
    await screen.findByRole('heading', { name: 'Promote Noémie to moderator' });
    await screen.findByText(
      'Are you certain you want to confirm this action ?',
    );

    const promoteModerator = await screen.findByRole('button', {
      name: 'Promote moderator',
    });
    await waitFor(() => {
      fireEvent.click(promoteModerator);
    });
    expect(fetchMock.called('/api/v1/users/6/')).toEqual(true);
    expect(fetchMock.lastOptions('/api/v1/users/6/')!.body).toEqual(
      '{"public_username":"Noémie","id":6,"role":"moderator"}',
    );
    // make sure current list gets updated
    expect(fetchMock.called('/api/v1/users/?role=student')).toEqual(true);
    expect(fetchMock.called('/api/v1/users/?role=moderator')).toEqual(true);
  });
});

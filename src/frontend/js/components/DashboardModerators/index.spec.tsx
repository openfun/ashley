import 'regenerator-runtime/runtime';
import fetchMock from 'fetch-mock';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { DashboardModerators } from '.';

jest.mock('../../data/frontEndData', () => ({
  appFrontendContext: { csrftoken: 'foo' },
}));

describe('<DashboardModerators />', () => {
  beforeEach(() => {
    fetchMock.get('/api/v1.0/users/?role=moderator', [
      { public_username: 'Samy', id: 9, roles: ['moderator'] },
    ]);
    fetchMock.get('/api/v1.0/users/?role=!moderator', [
      { public_username: 'Thérèse', id: 1, roles: ['student'] },
      { public_username: 'thomas', id: 2, roles: ['student'] },
      { public_username: 'Valérie', id: 3, roles: ['student'] },
      { public_username: 'Zao', id: 4, roles: ['student'] },
      { public_username: 'Thibaut', id: 5, roles: ['student'] },
      { public_username: 'Noémie', id: 6, roles: ['student'] },
      { public_username: 'Zackari', id: 7, roles: ['student'] },
      { public_username: 'Zoé', id: 8, roles: ['student'] },
    ]);
  });

  afterEach(() => {
    jest.resetAllMocks();
    fetchMock.reset();
  });

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
    fetchMock.mock(
      '/api/v1.0/users/6/',
      { status: 200, body: {} },
      { method: 'PUT' },
    );

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
    expect(fetchMock.called('/api/v1.0/users/6/')).toEqual(true);
    expect(fetchMock.lastOptions('/api/v1.0/users/6/')!.body).toEqual(
      '{"public_username":"Noémie","id":6,"roles":["student","moderator"]}',
    );
    // make sure current list gets updated
    expect(fetchMock.called('/api/v1.0/users/?role=!moderator')).toEqual(true);
    expect(fetchMock.called('/api/v1.0/users/?role=moderator')).toEqual(true);
  });
});
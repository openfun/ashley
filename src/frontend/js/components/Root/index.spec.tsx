import React from 'react';
import { IntlProvider } from 'react-intl';
import { getByText, render } from '@testing-library/react';
import { Root } from '.';

jest.mock('../DashboardModerators', () => ({
  __esModule: true,
  DashboardModerators: ({ exampleProp }: { exampleProp: string }) =>
    `This text should be render in the DashboardContainer ${exampleProp}`,
}));

describe('<Root />', () => {
  beforeEach(() => {
    jest.spyOn(console, 'warn').mockImplementation(() => {});
  });

  afterEach(jest.restoreAllMocks);
  it('finds all ashley-react containers and renders the relevant components into them with their passed props', () => {
    render(
      <IntlProvider locale="en">
        <Root ashleyReactSpots={[]} />
      </IntlProvider>,
    );
  });

  it('finds all ashley-react containers and renders the relevant components into them with their passed props', () => {
    // Create the containers for the component we're about to render
    const dashboardContainer = document.createElement('div');
    dashboardContainer.setAttribute(
      'class',
      'ashley-react ashley-react--DashboardModerators',
    );
    dashboardContainer.setAttribute(
      'data-props',
      JSON.stringify({ exampleProp: 'the prop value' }),
    );
    document.body.append(dashboardContainer);
    // Render the root component, passing the elements in need of frontend rendering
    render(
      <IntlProvider locale="en">
        <Root ashleyReactSpots={[dashboardContainer]} />
      </IntlProvider>,
    );
    getByText(
      dashboardContainer,
      'This text should be render in the DashboardContainer the prop value',
    );
  });

  it('prints a console warning and still renders everything else when it fails to find a component', () => {
    const dashboardContainer = document.createElement('div');
    dashboardContainer.setAttribute(
      'class',
      'ashley-react ashley-react--DashboardModerators',
    );
    document.body.append(dashboardContainer);
    // Create a component <UserFeedback /> that doesn't exists in Ashley
    const userFeedbackContainer = document.createElement('div');
    userFeedbackContainer.setAttribute(
      'class',
      'ashley-react ashley-react--user-feedback',
    );
    document.body.append(userFeedbackContainer);

    // Render the root component, passing our real element and our bogus one
    render(
      <IntlProvider locale="en">
        <Root ashleyReactSpots={[dashboardContainer, userFeedbackContainer]} />
      </IntlProvider>,
    );

    getByText(
      dashboardContainer,
      'This text should be render in the DashboardContainer undefined',
    );
    expect(userFeedbackContainer.innerHTML).toEqual('');
    expect(console.warn).toHaveBeenCalledWith(
      'Failed to load React component: no such component in Library UserFeedback',
    );
  });
});

import fetchMock from 'fetch-mock';
import { waitFor, fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { IntlProvider } from 'react-intl';
import { Actions } from '../../../types/Enums';
import { ButtonChangeRoleCta } from '.';

const props = {
  user: {
    public_username: 'Samuel',
    id: 2
  },
  action: Actions.PROMOTE,
  onChange: jest.fn(),
};
jest.mock('../../../data/frontEndData', () => ({
  appFrontendContext: { csrftoken: 'foo' },
  image_type: ['.gif', '.jpeg', '.jpg', '.png', '.svg'],
}));

describe('<ButtonChangeRoleCta />', () => {
  afterEach(() => {
    jest.resetAllMocks();
    fetchMock.reset();
  });

  it('renders a button with proper action text depending on props param and calls onChange prop', async () => {
    fetchMock.mock('/api/v1.0/users/2/', {});
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
      expect(fetchMock.called('/api/v1.0/users/2/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1.0/users/2/')!.body).toEqual(
      '{"public_username":"Samuel","id":2}',
    );
    expect(props.onChange).toHaveBeenCalled();
  });

  it('renders a button with proper action text depending on props param and calls onChange prop', async () => {
    fetchMock.mock('/api/v1.0/users/2/', {});
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
      expect(fetchMock.called('/api/v1.0/users/2/')).toEqual(true);
    });
    expect(fetchMock.lastOptions('/api/v1.0/users/2/')!.body).toEqual(
      '{"public_username":"Samuel","id":2}',
    );
    expect(props.onChange).toHaveBeenCalled();
  });
});

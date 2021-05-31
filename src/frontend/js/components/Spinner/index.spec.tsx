import { render, screen } from '@testing-library/react';
import React from 'react';

import { Spinner } from '.';

describe('<Spinner />', () => {
  it('displays spinner and have expected three div', () => {
    render(<Spinner />);
    screen.getByTestId('bounce1');
    screen.getByTestId('bounce2');
    screen.getByTestId('bounce3');
  });
});

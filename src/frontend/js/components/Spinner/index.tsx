import React from 'react';

export const Spinner = () => (
  <div className="spinner">
    <div className="spinner__bounce" data-testid="bounce1" />
    <div className="spinner__bounce" data-testid="bounce2" />
    <div className="spinner__bounce" data-testid="bounce3" />
  </div>
);

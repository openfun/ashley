import fetchMock from 'fetch-mock';
import { waitFor, render, screen } from '@testing-library/react';
import { EditorState } from 'draft-js';
import React from 'react';
import { IntlProvider } from 'react-intl';
import user from '@testing-library/user-event';
import { ImageAdd } from '.';
import { uploadFile } from '../../../utils/uploadFile';
const props = {
  editorState: new EditorState(),
  forum: 1,
  modifier: jest.fn(),
  onChange: jest.fn(),
  theme: {},
};

jest.mock('../../../data/frontEndData', () => ({
  appFrontendContext: {
    csrftoken: 'foo',
    max_upload: 1,
    image_type: ['.gif', '.jpeg', '.jpg', '.png', '.svg'],
  },
}));

jest.mock('../../../utils/uploadFile', () => ({
  uploadFile: jest.fn(),
}));

const mockUploadFile: jest.MockedFunction<
  typeof uploadFile
> = uploadFile as any;
describe('<ImageAdd />', () => {
  afterEach(() => {
    jest.resetAllMocks();
    fetchMock.reset();
  });

  it('renders component with expected element', async () => {
    render(
      <IntlProvider locale="en">
        <ImageAdd {...props} />
      </IntlProvider>,
    );
    screen.getByText('Add image');
    screen.getByLabelText('Add image');
  });

  it('renders component and upload image', async () => {
    fetchMock.mock('/api/v1.0/images/', { method: 'POST' });
    mockUploadFile.mockResolvedValue({
      id: 31,
      file: 'image.png',
      forum: 1,
    });
    render(
      <IntlProvider locale="en">
        <ImageAdd {...props} />
      </IntlProvider>,
    );
    const file = new File(['Jupiter'], 'Jupiter.png', { type: 'image/png' });
    const input = screen.getByLabelText('Add image') as HTMLInputElement;
    user.upload(input, file);
    expect(input.files![0]).toStrictEqual(file);

    await waitFor(() => expect(mockUploadFile).toHaveBeenCalled());
    expect(props.onChange).toHaveBeenCalled();
    expect(props.modifier).toHaveBeenCalled();
  });

  it('renders component and shows error on upload image if upload is not resolved', async () => {
    fetchMock.mock('/api/v1.0/images/', { method: 'POST' });
    render(
      <IntlProvider locale="en">
        <ImageAdd {...props} />
      </IntlProvider>,
    );
    const file = new File(['Mercure'], 'Mercure.png', { type: 'image/png' });
    const input = screen.getByLabelText('Add image') as HTMLInputElement;
    user.upload(input, file);
    expect(input.files![0]).toStrictEqual(file);

    await waitFor(() => expect(mockUploadFile).toHaveBeenCalled());

    screen.getByText(
      'An error occured uploading the image, please try again or contact the support',
    );
    expect(props.onChange).not.toHaveBeenCalled();
    expect(props.modifier).not.toHaveBeenCalled();
  });

  it('renders component and shows error on upload image that is too big', async () => {
    fetchMock.mock('/api/v1.0/images/', { method: 'POST' });
    render(
      <IntlProvider locale="en">
        <ImageAdd {...props} />
      </IntlProvider>,
    );
    const file = new File(['image'], 'image.png', { type: 'image/png' });
    Object.defineProperty(file, 'size', { value: 1024 * 1024 * 10 });

    const input = screen.getByLabelText('Add image') as HTMLInputElement;
    user.upload(input, file);
    expect(input.files![0]).toStrictEqual(file);

    await waitFor(() => expect(mockUploadFile).not.toHaveBeenCalled());

    screen.getByText(
      'An error occured uploading the image, the size of the file is over 1MB.',
    );
    expect(props.onChange).not.toHaveBeenCalled();
    expect(props.modifier).not.toHaveBeenCalled();
  });

  it('renders component and shows error on upload image with unauthorized extension', async () => {
    /**We can't select an image that is mp4 as it's filter with input file but we faint
     * to do it to make sure we have an error from the backend.
     */
    fetchMock.mock('/api/v1.0/images/', { method: 'POST' });
    render(
      <IntlProvider locale="en">
        <ImageAdd {...props} />
      </IntlProvider>,
    );
    const file = new File(['video'], 'video.mp4', { type: 'image/mp4' });

    const input = screen.getByLabelText('Add image') as HTMLInputElement;
    user.upload(input, file);
    expect(input.files![0]).toStrictEqual(file);

    await waitFor(() => expect(mockUploadFile).toHaveBeenCalled());

    screen.getByText(
      'An error occured uploading the image, please try again or contact the support',
    );
    expect(props.onChange).not.toHaveBeenCalled();
    expect(props.modifier).not.toHaveBeenCalled();
  });
});

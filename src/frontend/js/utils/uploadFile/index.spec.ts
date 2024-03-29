import { uploadFile } from '.';

describe('utils/uploadFile', () => {
  const mockProgressHandler = jest.fn();
  // tslint:disable:ban-types
  const callbacks: { [eventName: string]: Function } = {};
  const addEventListener = (eventName: string, callback: Function) => {
    callbacks[eventName] = callback;
  };
  const mockXHROpen = jest.fn();
  const mockXHRSend = jest.fn();
  const mockXHRInstance = {
    addEventListener,
    open: mockXHROpen,
    readyState: 0,
    send: mockXHRSend,
    status: 0,
    responseText: '',
    upload: { addEventListener },
  };
  const mockXHRClass = jest.fn(() => mockXHRInstance);

  beforeAll(() => {
    (window as any).XMLHttpRequest = mockXHRClass;
  });

  afterEach(jest.restoreAllMocks);

  it('makes an xhr POST to perform the upload, notifies of progress and resolves', async () => {
    // Creates the promise but don't await it so we can simulate the ongoing request
    const response = uploadFile(
      'https://example.com/upload',
      'some form data' as any,
      mockProgressHandler,
    );

    expect(mockXHROpen).toHaveBeenCalledWith(
      'POST',
      'https://example.com/upload',
    );
    expect(mockXHRSend).toHaveBeenCalledWith('some form data');

    callbacks.progress({ lengthComputable: true, loaded: 0, total: 200 });
    expect(mockProgressHandler).toHaveBeenLastCalledWith(0);

    callbacks.progress({ lengthComputable: true, loaded: 10, total: 200 });
    expect(mockProgressHandler).toHaveBeenLastCalledWith(5);

    callbacks.progress({ lengthComputable: true, loaded: 133.33, total: 200 });
    expect(mockProgressHandler).toHaveBeenLastCalledWith(66);

    callbacks.progress({ lengthComputable: true, loaded: 199.99, total: 200 });
    expect(mockProgressHandler).toHaveBeenLastCalledWith(99);

    callbacks.progress({ lengthComputable: true, loaded: 200, total: 200 });
    expect(mockProgressHandler).toHaveBeenLastCalledWith(100);

    // The request finishes and succeeds
    mockXHRInstance.readyState = 4;
    mockXHRInstance.status = 201;
    mockXHRInstance.responseText = '[{"result":"perfect"}]';
    callbacks.readystatechange();

    // Now we await the response to make sure it does resolve
    await expect(response).resolves.toEqual([{ result: 'perfect' }]);
  });

  it('rejects when the upload fails', async () => {
    // Creates the promise but don't await it so we can simulate the ongoing request
    const response = uploadFile(
      'https://example.com/upload',
      'some form data' as any,
      mockProgressHandler,
    );

    // The request finishes and fails
    mockXHRInstance.readyState = 4;
    mockXHRInstance.status = 400;
    callbacks.readystatechange();

    await expect(response).rejects.toEqual(
      new Error('Failed to perform the upload on https://example.com/upload.'),
    );
  });
});

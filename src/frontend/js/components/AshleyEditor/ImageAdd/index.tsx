import React, { useEffect, useRef, useState } from 'react';
import { FormattedMessage } from 'react-intl';
import { EditorState } from 'draft-js';
import { DraftJsButtonTheme } from '@draft-js-plugins/buttons';
import { appFrontendContext } from './../../../data/frontEndData';
import { FileUploadError } from './../../../types/Enums';
import { uploadFile } from './../../../utils/uploadFile';
import { messagesEditor } from '../messages';
import { UploadedFile } from '../../../types/UploadedFile';
import { Spinner } from '../../Spinner';

interface ImageAddProps {
  editorState: EditorState;
  onChange(editorState: EditorState): void;
  modifier(
    editorState: EditorState,
    url: string,
    extraData: Record<string, unknown>,
  ): EditorState;
  forum: number;
  theme: DraftJsButtonTheme;
}

export const ImageAdd = (props: ImageAddProps) => {
  const [open, setOpen] = useState(false);
  const [errorOnUpload, setErrorOnUpload] = useState(FileUploadError.NONE);
  const [isImageLoading, setIsImageLoading] = useState(false);
  const node = useRef<HTMLDivElement>(null);

  const togglePopover = () => {
    if (!open) {
      setErrorOnUpload(FileUploadError.NONE);
    }
    // if we click on the button to open the pop up while it's already open,
    // it then needs to be closed
    setOpen(!open);
  };
  const closePopover = (e: MouseEvent) => {
    if (!node.current?.contains(e.target as Node)) {
      setOpen(false);
    }
  };

  useEffect(() => {
    document.addEventListener('click', closePopover);
    return () => {
      document.removeEventListener('click', closePopover);
    };
  }, []);

  const selectImage = (event: React.ChangeEvent<HTMLInputElement>): void => {
    const { files } = event.target;
    if (files?.length) {
      const file = files[0];
      if (file.size > appFrontendContext.max_upload * 1024 * 1024) {
        setErrorOnUpload(FileUploadError.MAX_UPLOAD);
      } else {
        uploadImage(file);
        // if user wants to upload the same image again
        event.target.value = '';
      }
    }
  };

  const uploadImage = async (file: File) => {
    setIsImageLoading(true);
    const formData = new FormData();
    formData.append('forum', JSON.stringify(props.forum));
    formData.append('file', file);
    formData.append('csrfmiddlewaretoken', appFrontendContext.csrftoken);
    try {
      const upload = await uploadFile('/api/v1.0/images/', formData);
      setIsImageLoading(false);
      props.onChange(props.modifier(props.editorState, upload.file, {}));
      setOpen(false);
    } catch (error) {
      setErrorOnUpload(FileUploadError.ERROR);
    }
  };

  const popoverClassName = open
    ? 'add-image-popover'
    : 'add-image-closed-popover';
  const buttonClassName = open ? 'add-image-pressed-button' : '';
  const isErrorOn = errorOnUpload !== FileUploadError.NONE;
  const listTypeAllowed = appFrontendContext.image_type
    .map((ext) => '.' + ext)
    .join(',');
  const { buttonWrapper = '', button } = props.theme;

  return (
    <div className={buttonWrapper} ref={node}>
      <button
        data-testid="addImage"
        className={`${buttonClassName} ${button} fa fa-image`}
        onClick={togglePopover}
        type="button"
      ></button>
      <div className={popoverClassName} data-testid="popAddImage">
        <div className="image-modal">
          <div className="image-modal__header">
            <span className="image-modal__header__option">
              <FormattedMessage {...messagesEditor.addImageFileUploadTitle} />
              <span className="image-modal__header__label image-modal__header__label__highlighted"></span>
            </span>
          </div>

          {!isErrorOn ? (
            <div>
              <div className="image-modal__option">
                {!isImageLoading ? (
                  <label htmlFor="file" className="image-modal__option__label">
                    <FormattedMessage
                      {...messagesEditor.addImageFromComputer}
                    />
                  </label>
                ) : (
                  <div className="image-modal__spinner">
                    <Spinner />
                  </div>
                )}
              </div>
              <input
                type="file"
                id="file"
                accept={listTypeAllowed}
                onChange={selectImage}
                className="image-modal__option__input"
              />
            </div>
          ) : (
            <span>
              {errorOnUpload === FileUploadError.MAX_UPLOAD ? (
                <FormattedMessage
                  {...messagesEditor.addImageFromComputerErrorMaxUpload}
                  values={{ maxSize: appFrontendContext.max_upload }}
                />
              ) : (
                <FormattedMessage
                  {...messagesEditor.addImageFromComputerError}
                />
              )}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

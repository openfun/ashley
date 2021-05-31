import { defineMessages } from 'react-intl';

export const messagesEditor = defineMessages({
  addImageFromComputer: {
    defaultMessage: 'Add image',
    description: 'Title for the button to upload an image.',
    id: 'components.AshleyEditor.ImageAdd.addImageFromComputer',
  },
  addImageFromComputerError: {
    defaultMessage:
      'An error occured uploading the image, please try again or contact the support',
    description: 'Error message on uploading image',
    id: 'components.AshleyEditor.ImageAdd.addImageFromComputerError',
  },
  addImageFromComputerErrorMaxUpload: {
    defaultMessage:
      'An error occured uploading the image, the size of the file is over {maxSize}MB.',
    description: 'Error message on uploading image, max size reached',
    id: 'components.AshleyEditor.ImageAdd.addImageFromComputerErrorMaxUpload',
  },
  addImageFileUploadTitle: {
    defaultMessage: 'Upload Image',
    description: 'Title for the modal to upload an image.',
    id: 'components.AshleyEditor.ImageAdd.addImageFileUploadTitle',
  },
  linkPlaceholderEditor: {
    defaultMessage: 'Fill-in or paste your URL here and press enter',
    description: 'Placeholder when adding a link in the editor',
    id: 'components.AshleyEditor.linkPlaceholderEditor',
  },
  placeholderEditor: {
    defaultMessage: 'Please enter your message here...',
    description: 'Placeholder for new posts when editor is empty',
    id: 'components.AshleyEditor.placeholderEditor',
  },
});

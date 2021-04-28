import React, { Component } from 'react';
import { EditorState } from 'draft-js';

interface ImageAddProps {
  editorState: EditorState;
  onChange(editorState: EditorState): void;
  modifier(
    editorState: EditorState,
    url: string,
    extraData: Record<string, unknown>,
  ): EditorState;
}
export default class ImageAdd extends React.Component<ImageAddProps> {
  // Start the popover closed
  state = {
    url: '',
    open: false,
  };
  preventNextClose = false;
  // When the popover is open and users click anywhere on the page,
  // the popover should close
  componentDidMount() {
    document.addEventListener('click', this.closePopover);
  }

  componentWillUnmount() {
    document.removeEventListener('click', this.closePopover);
  }

  // Note: make sure whenever a click happens within the popover it is not closed
  onPopoverClick = () => {
    this.preventNextClose = true;
  };

  openPopover = () => {
    if (!this.state.open) {
      this.preventNextClose = true;
      this.setState({
        open: true,
      });
    }
  };

  closePopover = () => {
    if (!this.preventNextClose && this.state.open) {
      this.setState({
        open: false,
      });
    }

    this.preventNextClose = false;
  };

  addImage = () => {
    const { editorState, onChange } = this.props as ImageAddProps;
    onChange(this.props.modifier(editorState, this.state.url, this.state));
  };

  changeUrl = (evt: React.ChangeEvent<HTMLInputElement>) => {
    this.setState({ url: evt.target.value });
  };

  render() {
    const popoverClassName = this.state.open
      ? 'addImagePopover'
      : 'addImageClosedPopover';
    const buttonClassName = this.state.open
      ? 'addImagePressedButton'
      : '';
    return (
      <div className='bi09khh'>
        <button
          className={`${buttonClassName} bc4rxid fa fa-image`}
          onMouseUp={this.openPopover}
          type="button"
        >
        </button>
        <div className={popoverClassName} onClick={this.onPopoverClick}>
          <input
            type="text"
            placeholder="todotranslate Paste the image url …"
            className="addImageInput"
            onChange={this.changeUrl}
            value={this.state.url}
          />
          <button
            className="addImageConfirmButton btn btn-primary"
            type="button"
            onClick={this.addImage}
          >
            OK
          </button>
        </div>
      </div>
    );
  }
}

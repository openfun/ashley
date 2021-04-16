import React from 'react';
import { ButtonChangeRoleCta } from '../ButtonChangeRoleCta';
import { messagesDashboardModerators } from '../messages';
import { FormattedMessage, useIntl } from 'react-intl';
import { User } from '../../../types/User';
import { Actions } from '../../../types/Enums';
import ReactModal from 'react-modal';

export interface ModalProps {
  user: User | undefined;
  action: Actions;
  modalIsOpen: boolean;
  appElement: string;
  setModalIsOpen: (value: boolean) => void;
  onChange: () => void;
}

export const Modal = (props: ModalProps) => {
  const intl = useIntl();
  ReactModal.setAppElement(props.appElement);

  const message =
    props.action === Actions.PROMOTE
      ? messagesDashboardModerators.modalPromoteTitle
      : messagesDashboardModerators.modalRevokeTitle;
  return (
    <ReactModal
      className="modal-dialog"
      isOpen={props.modalIsOpen}
      onRequestClose={() => props.setModalIsOpen(false)}
      overlayClassName="modal-overlay"
    >
      <div className="modal-content">
        <div className="modal-header">
          {props.user && (
            <h4 className="modal-title">
              <FormattedMessage
                {...message}
                values={{ userName: props.user.public_username }}
              />
            </h4>
          )}
          <button
            type="button"
            className="modal-close"
            aria-label={intl.formatMessage(
              messagesDashboardModerators.closeButton,
            )}
            onClick={() => props.setModalIsOpen(false)}
          >
            <span aria-hidden="true">x</span>
          </button>
        </div>
        <div className="modal-body">
          <FormattedMessage
            {...messagesDashboardModerators.modalConfirmation}
          />
        </div>
        <div className="modal-footer">
          {props.user && (
            <ButtonChangeRoleCta
              action={props.action}
              user={props.user}
              onChange={props.onChange}
            />
          )}
          <button
            className="btn modal-cancel"
            onClick={() => props.setModalIsOpen(false)}
          >
            <FormattedMessage {...messagesDashboardModerators.closeButton} />
          </button>
        </div>
      </div>
    </ReactModal>
  );
};

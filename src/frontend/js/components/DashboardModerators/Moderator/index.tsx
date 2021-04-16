import React from 'react';
import { FormattedMessage, useIntl } from 'react-intl';
import { User } from '../../../types/User';
import { messagesDashboardModerators } from '../messages';

export interface ModeratorProps {
  user: User;
  onClick: (user: User) => void;
}

export const Moderator = (props: ModeratorProps) => {
  const intl = useIntl();
  return (
    <div className="mt-2 mb-1">
      <div className="row">
        <div className="col-md-2 offset-md-2">
          <div className="username">
            <a
              href={`/forum/member/profile/${props.user.id}`}
              title={intl.formatMessage(
                messagesDashboardModerators.accessProfilModeratorTitle,
                { userName: props.user.public_username },
              )}
            >
              {props.user.public_username}
            </a>
          </div>
        </div>
        <div className="col-md-7 moderator-sidebar">
          <button
            className="btn btn-primary"
            onClick={() => props.onClick(props.user)}
          >
            <FormattedMessage
              {...messagesDashboardModerators.revokeModerator}
            />
          </button>
        </div>
      </div>
    </div>
  );
};

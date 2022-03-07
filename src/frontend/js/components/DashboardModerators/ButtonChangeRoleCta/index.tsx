import React from 'react';
import { FormattedMessage } from 'react-intl';
import { messagesDashboardModerators } from '../messages';
import { Actions } from '../../../types/Enums';
import { User } from '../../../types/User';
import { handleUserModeratorGroup } from '../../../data/fetchApi';

export interface ButtonChangeRoleCtaProps {
  user: User;
  action: Actions;
  onChange: () => void;
}

export const ButtonChangeRoleCta = ({
  user,
  action,
  onChange,
}: ButtonChangeRoleCtaProps) => {
  const message =
    action === Actions.PROMOTE
      ? messagesDashboardModerators.promoteModerator
      : messagesDashboardModerators.revokeModerator;

  const updateStudent = async () => {
    const content = await handleUserModeratorGroup(user, action);
    onChange();
    return content;
  };

  return (
    <button
      onClick={updateStudent}
      id="add-moderator__cta"
      className="btn btn-primary"
    >
      <FormattedMessage {...message} />
    </button>
  );
};

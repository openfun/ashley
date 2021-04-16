import React from 'react';
import { FormattedMessage } from 'react-intl';
import { messagesDashboardModerators } from '../messages';
import { Actions, Role } from '../../../types/Enums';
import { User } from '../../../types/User';
import { updateUser } from '../../../data/fetchApi';

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
    // Depending on action submit the requested role
    switch (action) {
      case Actions.PROMOTE:
        user.roles.push(Role.MODERATOR);
        break;
      case Actions.REVOKE:
        const index = user.roles.indexOf(Role.MODERATOR);
        if (index > -1) {
          user.roles.splice(index, 1);
        }
        break;
    }
    const content = await updateUser(user);
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

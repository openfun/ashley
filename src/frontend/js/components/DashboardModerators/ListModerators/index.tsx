import React from 'react';
import { FormattedMessage } from 'react-intl';
import { User } from '../../../types/User';
import { Moderator } from '../Moderator';
import { messagesDashboardModerators } from '../messages';

export interface ListModeratorsProps {
  users: User[];
  onChange: () => void;
  setUser: (value: User) => void;
  totalUsers: number;
}

export const ListModerators = (props: ListModeratorsProps) => {
  const handleOnChange = (user: User) => {
    props.setUser(user);
    props.onChange();
  };
  return (
    <div className="row mb-3 profile">
      <div className="col-8 profile-content">
        <div className="card">
          <div className="card-header">
            <FormattedMessage
              {...messagesDashboardModerators.amountModerator}
              values={{
                moderatorCount: props.users.length,
                userCount: props.totalUsers,
              }}
            />
          </div>
          {props.users.map((user, key) => {
            return (
              <Moderator
                key={`${user.id}`}
                user={user}
                onClick={handleOnChange}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

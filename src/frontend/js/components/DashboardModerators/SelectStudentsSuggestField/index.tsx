import React, { useState } from 'react';
import { FormattedMessage, useIntl } from 'react-intl';
import AutoSuggest from 'react-autosuggest';
import { messagesDashboardModerators } from '../messages';
import { User } from '../../../types/User';

const SUGGESTION_TO_SHOW = 5;

export interface SelectStudentsSuggestFieldProps {
  users: User[];
  onChange: () => void;
  setUser: (value: User) => void;
}

export const SelectStudentsSuggestField = (
  props: SelectStudentsSuggestFieldProps,
) => {
  const intl = useIntl();
  const [value, setValue] = useState('');
  // init and sort by alphabetic order user suggestions
  const [suggestions, setSuggestions] = useState<User[]>(
    props.users.sort((a, b) =>
      a.public_username.localeCompare(b.public_username),
    ),
  );

  const getSuggestionValue = (suggestion: User) => {
    props.setUser(suggestion);
    return suggestion.public_username;
  };

  const getSuggestions = (text: string): User[] => {
    const propsFitered = props.users.filter((user) =>
      user.public_username.toLowerCase().startsWith(text.trim().toLowerCase()),
    );
    return propsFitered.length > 0
      ? propsFitered.slice(0, SUGGESTION_TO_SHOW)
      : props.users.slice(0, SUGGESTION_TO_SHOW);
  };

  return (
    <div className="mb-3 row">
      <div className="col-8 profile-content">
        <div className="card">
          <div className="card-header">
            <FormattedMessage
              {...messagesDashboardModerators.addNewModerator}
              values={{ studentCount: props.users.length }}
            />
          </div>
          <div className="row my-3">
            <div className="col-md-9 offset-md-2">
              <AutoSuggest
                suggestions={suggestions}
                onSuggestionsClearRequested={() => setSuggestions([])}
                // tslint:disable: no-shadowed-variable
                onSuggestionsFetchRequested={({ value }) => {
                  setValue(value);
                  setSuggestions(getSuggestions(value));
                }}
                onSuggestionSelected={() => {
                  props.onChange();
                  setValue('');
                }}
                getSuggestionValue={getSuggestionValue}
                renderSuggestion={(suggestion: User) => (
                  <span>{suggestion.public_username}</span>
                )}
                inputProps={{
                  placeholder: intl.formatMessage(
                    messagesDashboardModerators.searchFieldPlaceholder,
                  ),
                  value,
                  onChange: (_, { newValue }) => {
                    setValue(newValue);
                  },
                }}
                shouldRenderSuggestions={(v: string) => {
                  return v.length > 0;
                }}
                highlightFirstSuggestion={true}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import { defineMessages } from 'react-intl';

export const messagesDashboardModerators = defineMessages({
  addNewModerator: {
    defaultMessage:
      'Add new moderator to the forum : {studentCount, number} {studentCount, plural, one {student} other {students}} found',
    description:
      "Present the block where the input to search students is, sum up information on number of students left that aren' moderators. Appears just above search input",
    id: 'components.DashboardModerators.SearchModeratorSuggestField.addNewModerator',
  },
  amountModerator: {
    defaultMessage:
      '{moderatorCount, number} {moderatorCount, plural, one {moderator} other {moderators}} moderators found from {userCount, number} {userCount, plural, one {user} other {users}} found',
    description:
      'Present the block where the list of moderator is, sum up information on number of moderator compare to amount of total users that could be moderators. Appears just above results',
    id: 'components.DashboardModerators.ListModerators.amountModerator',
  },
  closeButton: {
    defaultMessage: 'Close',
    description:
      'Text for the button to close the modal to promote or revoke a user to moderator',
    id: 'components.DashboardModerators.Modal.closeModal',
  },
  modalConfirmation: {
    defaultMessage: 'Are you certain you want to confirm this action ? ',
    description:
      'Body for the modal to promote or revoke the defined user to moderator, to ask the user to confirm this action.',
    id: 'components.DashboardModerators.ButtonChangeRoleCta.modalConfirmation',
  },
  modalPromoteTitle: {
    defaultMessage: 'Promote {userName} to moderator',
    description:
      'Title for the modal to promote the defined user to moderator of the forum.',
    id: 'components.DashboardModerators.ButtonChangeRoleCta.modalPromoteTitle',
  },
  modalRevokeTitle: {
    defaultMessage: 'Revoke {userName} to moderator',
    description:
      'Title for the modal to revoke the defined user to moderator of the forum.',
    id: 'components.DashboardModerators.ButtonChangeRoleCta.modalRevokeTitle',
  },
  promoteModerator: {
    defaultMessage: 'Promote moderator',
    description: 'CTA for students to promote moderators',
    id: 'components.DashboardModerators.SearchModeratorSuggestField.promote.cta',
  },
  revokeModerator: {
    defaultMessage: 'Revoke moderator',
    description: 'CTA for moderators to be revoked',
    id: 'components.DashboardModerators.SearchModeratorSuggestField.revoke.cta',
  },
  searchFieldPlaceholder: {
    defaultMessage: 'Search for students',
    description:
      'Placeholder text displayed in the search field when it is empty.',
    id: 'components.DashboardModerators.SearchModeratorSuggestField.searchFieldPlaceholder',
  },
});

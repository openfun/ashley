import { appFrontendContext } from './frontEndData';
import { User } from '../types/User';
import { Actions, filterApiRole } from '../types/Enums';
import { handle } from '../utils/errors/handle';

/**
 * Request API to fetch list data
 */
export const fetchUsers = async (role: filterApiRole) => {
  let response: Response;
  try {
    response = await fetch(`/api/v1.0/users/?role=` + role, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    return handle(error);
  }
  if (!response.ok) {
    return handle(
      new Error(`Failed to load  ${role} list: ${response.status}.`),
    );
  }
  try {
    return await response.json();
  } catch (error) {
    handle(new Error(`Failed to decode JSON in list ${role}: ${error}`));
  }
};

/**
 * Request API to add group moderator for this student
 *
 */
export const handleUserModeratorGroup = async (user: User, action: Actions) => {
  let response: Response;
  try {
    response = await fetch(`/api/v1.0/users/${user.id}/${action}/`, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': appFrontendContext.csrftoken,
      },
      method: 'PATCH',
    });
  } catch (error) {
    return handle(new Error(`Failed to updateUser ${error}`));
  }
  if (!response.ok) {
    return handle(new Error(`Failed to update student : ${response.status}.`));
  }
  try {
    return await response.json();
  } catch (error) {
    return handle(new Error(`Failed to decode JSON in updateUser ${error}`));
  }
};

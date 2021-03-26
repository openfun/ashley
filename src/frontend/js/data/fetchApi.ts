import { appFrontendContext } from './frontEndData';
import { User } from '../types/User';
import { Role } from '../types/Enums';
import { handle } from '../utils/errors/handle';

/**
 * Request API to fetch list data
 */
export const fetchUsers = async (role: Role) => {
  let response: Response;
  try {
    response = await fetch(`/api/v1/users/?role=` + role, {
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
 */
export const updateUser = async (user: User) => {
  let response: Response;
  try {
    response = await fetch(`/api/v1/users/${user.id}/`, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFTOKEN': appFrontendContext.csrftoken,
      },
      body: JSON.stringify(user),
      method: 'PUT',
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

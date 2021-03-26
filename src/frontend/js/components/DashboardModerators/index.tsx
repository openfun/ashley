import React, { useState } from 'react';
import { User } from '../../types/User';
import { Actions, Role } from '../../types/Enums';
import { SelectStudentsSuggestField } from './SelectStudentsSuggestField';
import { ListModerators } from './ListModerators';
import { Modal } from './Modal';
import { fetchUsers } from '../../data/fetchApi';
import { useAsyncEffect } from '../../utils/useAsyncEffect';
import { handle } from '../../utils/errors/handle';

export const DashboardModerators = () => {
  const [listModerator, setListModerator] = useState<User[]>([]);
  const [listStudent, setListStudent] = useState<User[]>([]);
  const [modalIsOpen, setModalIsOpen] = useState(false);
  const [user, setUser] = useState<User>();
  const [kind, setKind] = useState<Actions>();
  /* id in which we load the modal */
  const appElement = '#modal-exclude__react';
  /* update list moderators */
  const fetchListModerators = async () => {
    setListModerator(await fetchUsers(Role.MODERATOR));
  };
  /* update list student */
  const fetchListStudents = async () => {
    setListStudent(await fetchUsers(Role.STUDENT));
  };
  /* set list moderators and students */
  useAsyncEffect(async () => {
    try {
      await fetchListModerators();
      await fetchListStudents();
    } catch (error) {
      handle(error);
    }
  }, []);

  const handleOnSelectUser = (action: Actions) => {
    setModalIsOpen(true);
    setKind(action);
  };
  const handleOnConfirm = async () => {
    await fetchListModerators();
    await fetchListStudents();
    setModalIsOpen(false);
  };

  return (
    <React.Fragment>
      <SelectStudentsSuggestField
        setUser={setUser}
        users={listStudent!}
        onChange={() => handleOnSelectUser(Actions.PROMOTE)}
      />
      <ListModerators
        setUser={setUser}
        users={listModerator}
        totalUsers={listStudent.length + listModerator.length}
        onChange={() => handleOnSelectUser(Actions.REVOKE)}
      />
      <Modal
        appElement={appElement}
        user={user}
        action={kind!}
        modalIsOpen={modalIsOpen}
        onChange={handleOnConfirm}
        setModalIsOpen={setModalIsOpen}
      />
    </React.Fragment>
  );
};

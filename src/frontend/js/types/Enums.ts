export enum Actions {
  REVOKE = 'remove_group_moderator',
  PROMOTE = 'add_group_moderator',
}
export enum DraftHandleValue {
  HANDLED = 'handled',
  NOT_HANDLED = 'not-handled',
}

export enum Role {
  MODERATOR = 'moderator',
}

export enum filterApiRole {
  NOT_MODERATOR = '!moderator',
  MODERATOR = 'moderator',
}

export enum FileUploadError {
  NONE = 'NONE',
  MAX_UPLOAD = 'MAX_UPLOAD',
  ERROR = 'ERROR',
}

export enum TypeLatexStyle {
  INLINE = 'inline',
  BLOCK = 'block',
}

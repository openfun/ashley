/**
 * Generic error handler to be called whenever we need to do error reporting throughout the app.
 * Logs the error to the console.
 */
export const handle = (error: Error) => {
  // tslint:disable: no-console
  console.log(error);
};

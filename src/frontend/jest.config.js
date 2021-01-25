module.exports = {
  moduleFileExtensions: ['ts', 'tsx', 'js', 'css'],
  setupFilesAfterEnv: ['./testSetup.ts'],
  testMatch: [__dirname + '/**/*.spec.+(ts|tsx|js)'],
  testURL: 'https://localhost',
};

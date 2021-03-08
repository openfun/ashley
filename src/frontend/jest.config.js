module.exports = {
  moduleFileExtensions: ['ts', 'tsx', 'js', 'css'],
  setupFilesAfterEnv: ['./testSetup.ts'],
  testMatch: [__dirname + '/js/**/*.spec.+(ts|tsx|js)'],
  testURL: 'https://localhost',
  transformIgnorePatterns: ['node_modules/(?!(lodash-es)/)'],
};

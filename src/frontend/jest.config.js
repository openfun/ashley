const path = require('path');
module.exports = {
  moduleFileExtensions: ['css', 'js', 'ts', 'tsx'],
  setupFilesAfterEnv: ['./testSetup.ts', 'regenerator-runtime/runtime'],
  testMatch: [__dirname + '/js/**/*.spec.+(ts|tsx|js)'],
  testURL: 'https://localhost',
  transformIgnorePatterns: [
    '/node_modules/(?!(lodash-es|draft-js-latex-plugin)/)',
  ],
};

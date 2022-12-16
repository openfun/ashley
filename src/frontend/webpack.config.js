const path = require('path');

module.exports = () => {
  const babelCompileDeps = ['react-intl', 'react-modal'];

  const config = {
    // Disable production-specific optimizations by default
    // They can be re-enabled by running the cli with `--mode=production` or making a separate
    // webpack config for production.
    mode: 'development',

    entry: [
      'regenerator-runtime/runtime',
      path.resolve(__dirname, 'js', 'ashley.ts'),
      path.resolve(__dirname, 'js', 'index.tsx'),
    ],

    output: {
      filename: 'ashley.js',
      path: path.join(__dirname, '/../ashley/static/ashley/js/build'),
      // `chunkFilename` must have a unique and different name on each build. This will prevent overwriting
      // of existing chunks if backend static storage is on AWS.
      chunkFilename: '[id].[fullhash].index.js',
      clean: true,
    },

    // Enable sourcemaps for debugging webpack's output.
    devtool: 'source-map',

    resolve: {
      // Add '.ts' and '.tsx' as resolvable extensions.
      extensions: ['.ts', '.tsx', '.js', '.json'],
    },

    module: {
      rules: [
        {
          test: /\.(woff|woff2|ttf|eot|png|jpg|svg|gif)$/i,
          use: ['file-loader'],
        },
        { test: /\.css$/, use: ['style-loader', 'css-loader'] },
        {
          test: new RegExp(`(${babelCompileDeps.join('|')}.*)`),
          use: [
            {
              loader: 'babel-loader',
              options: {
                plugins: [
                  ...require('./babel.config').plugins,
                  // Some modules are not pre-compiled but do not use import/export
                  // We need to give webpack
                  '@babel/plugin-transform-modules-commonjs',
                ],
                presets: require('./babel.config').presets,
              },
            },
          ],
        },
        {
          exclude: /node_modules/,
          test: new RegExp(`\.(tsx?|jsx?)$`),
          use: [
            {
              loader: 'babel-loader',
              options: require('./babel.config'),
            },
          ],
        },
        // All output '.js' files will have any sourcemaps re-processed by 'source-map-loader'.
        { enforce: 'pre', test: /\.js$/, loader: 'source-map-loader' },
      ],
    },
  };

  return config;
};

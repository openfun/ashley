module.exports = {
  // Disable production-specific optimizations by default
  // They can be re-enabled by running the cli with `--mode=production` or making a separate
  // webpack config for production.
  mode: 'development',

  // Currently, @babel/preset-env is unaware that using import() with Webpack relies on Promise internally.
  // Environments which do not have builtin support for Promise, like Internet Explorer, will require both
  // the promise and iterator polyfills be added manually.
  entry: ['./js/ashley.ts'],

  // chunkFilename must have a unique and different name on each build
  // this will prevent to replace existing chunk if backend static storage
  // is on AWS.
  output: {
    filename: 'ashley.js',
    path: __dirname + '/../ashley/static/ashley/js',
    chunkFilename: '[id].[hash].index.js',
  },

  // Enable sourcemaps for debugging webpack's output.
  devtool: 'source-map',

  resolve: {
    // Add '.ts' and '.tsx' as resolvable extensions.
    extensions: ['.ts', '.tsx', '.js', '.json'],
  },

  module: {
    rules: [
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
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

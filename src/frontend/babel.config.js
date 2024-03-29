module.exports = {
  plugins: [
    [
      'react-intl',
      {
        ast: true,
        extractFromFormatMessageCall: true,
        idInterpolationPattern: '[sha512:contenthash:base64:6]',
      },
    ],
    ['@babel/proposal-class-properties'],
    ['@babel/plugin-syntax-dynamic-import'],
  ],
  presets: [
    [
      '@babel/preset-env',
      {
        corejs: 3,
        forceAllTransforms: true,
        targets: 'last 1 version, >0.2%, IE 11',
        useBuiltIns: 'entry',
      },
    ],
    '@babel/preset-typescript',
    'react',
  ],
};

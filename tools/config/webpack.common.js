const path = require('path');
const webpack = require('webpack');

module.exports = {
  context: path.resolve(__dirname, '../../frontend'),

  entry: {
    app: './js/app.js',
  },

  output: {
    path: path.resolve(__dirname, '../../conditional/static'),
    filename: '[name].js',
    publicPath: '/static/',
  },

  module: {
    rules: [
      {
        test: /\.js$/,
        use: [{
          loader: 'babel-loader',
          options: {
            'presets': ['es2015'],
          },
        }, {
          loader: 'eslint-loader'
        }],
      },
      {
        test: require.resolve('jquery'),
        use: [{
          loader: 'expose-loader',
          options: 'jQuery'
        }, {
          loader: 'expose-loader',
          options: '$'
        }],
      },
      {
        test: /bootstrap-material-datetimepicker/,
        use: [{
          loader: 'imports-loader',
          options: 'moment',
        }],
      },
      {
        test: /simple-masonry/,
        use: [{
          loader: 'imports-loader',
          options: 'define=>false',
        }],
      },
      {
        test: /\.(ttf|eot|woff|woff2|svg)$/,
        loader: 'file-loader',
        options: {
          name: 'fonts/bootstrap/[name].[ext]',
        },
      },
    ],
  },

  resolve: {
    modules: [
      'node_modules',
      path.resolve(__dirname, '../../frontend/js'),
    ],
    extensions: ['.js', '.json']
  },

  target: 'web',

  plugins: [
    new webpack.ProgressPlugin({ profile: false }),
  ],
};

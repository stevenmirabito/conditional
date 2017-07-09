const path = require('path');

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
        test: /\.s?(a|c)ss$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].css',
              outputPath: 'css/',
              publicPath: '/static/css/',
            }
          },
          'extract-loader',
          {
            loader: 'css-loader',
            options: {
              sourceMap: true
            }
          },
          {
            loader: 'postcss-loader',
            options: {
              sourceMap: true,
              plugins: [
                require('autoprefixer')(),
                require('cssnano')(),
              ],
            },
          },
          {
            loader: 'sass-loader',
            options: {
              sourceMap: true,
            },
          },
        ],
      },
      {
        test: /\.(ttf|eot|woff|woff2|svg)$/,
        loader: 'file-loader',
        options: {
          name: 'fonts/[name].[ext]',
        },
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
};

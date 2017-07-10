const Merge = require('webpack-merge');
const CommonConfig = require('./webpack.common.js');

module.exports = Merge.smart(CommonConfig, {
  module: {
    rules: [
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
    ],
  },

  devtool: 'cheap-module-source-map',

  devServer: {
    compress: true,
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/': 'http://backend:6969',
    },
  },
});

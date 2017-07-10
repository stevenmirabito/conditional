const webpack = require('webpack');
const Merge = require('webpack-merge');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');
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
              name: '[name].[hash].css',
              outputPath: 'css/',
              publicPath: '/static/css/',
            }
          },
          'extract-loader',
          'css-loader',
          {
            loader: 'postcss-loader',
            options: {
              sourceMap: false,
              plugins: [
                require('autoprefixer')(),
                require('cssnano')(),
              ],
            },
          },
          'sass-loader',
        ],
      },
    ],
  },

  output: {
    filename: '[name].[hash].js',
  },

  plugins: [
    new ManifestPlugin({
      basePath: '/static/',
    }),
    new UglifyJSPlugin(),
    new webpack.NoEmitOnErrorsPlugin()
  ]
});

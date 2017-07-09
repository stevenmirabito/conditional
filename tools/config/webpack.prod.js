const Merge = require('webpack-merge');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin');
const CommonConfig = require('./webpack.common.js');

module.exports = Merge(CommonConfig, {
  output: {
    filename: '[name].[hash].js',
  },

  plugins: [
    new UglifyJSPlugin(),
    new webpack.NoEmitOnErrorsPlugin()
  ]
});

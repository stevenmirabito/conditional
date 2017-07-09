const Merge = require('webpack-merge');
const CommonConfig = require('./webpack.common.js');

module.exports = Merge(CommonConfig, {
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

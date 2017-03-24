var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  entry: [
    'babel-polyfill',
    path.resolve(__dirname, 'src', 'app', 'index.js')
  ],
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist'),
    publicPath : ''
  },
  devServer: {
    historyApiFallback: true
  },
  module: {
    loaders: [{
      test: /\.css$/,
      loader: "style-loader!css-loader"
    }, {
      test: /\.html$/,
      loader: "file?name=[name].[ext]"
    }, {
      test: /\.js$|\.jsx?$/,
      loaders: ['babel-loader'],
      exclude: [/node_modules/]
    }, {
      test: /worker\.js$/,
      loaders: ['worker-loader', 'babel-loader']
    }, {
      test: /\.(eot|gif|png|svg|ttf|woff(2)?)(\?v=\d+\.\d+\.\d+)?/,
      loader: 'url-loader'
    }]
  },
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {
        API_URL: process.env.API_URL && `'${process.env.API_URL}'`
      }
    }),
    new HtmlWebpackPlugin({
      template: './index.web.ejs'
    }),
    new CopyWebpackPlugin([{
      to: 'images',
      from: 'images'
    }])
  ],
  resolve: {
    root: [
      path.resolve(__dirname, 'src')
    ],
    extensions: ['', '.js', '.jsx', '.json'],
  },
};

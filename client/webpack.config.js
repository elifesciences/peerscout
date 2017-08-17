const fs = require('fs');
var path = require('path');
var webpack = require('webpack');
var HtmlWebpackPlugin = require('html-webpack-plugin');
var CopyWebpackPlugin = require('copy-webpack-plugin');

const API_URL = process.env.API_URL || (
  process.env.NODE_ENV == 'development' && 'http://localhost:8080/api'
) || '';

inject_html_head = []
inject_html_body = []
inject_html_end = []

inject_html_dir = path.resolve(__dirname, '.inject-html');
if (fs.existsSync(inject_html_dir)) {
  const filenames = fs.readdirSync(inject_html_dir);
  filenames.sort();
  filenames.forEach(fn => {
    console.log('adding inject html:', fn);
    const content = fs.readFileSync(path.resolve(inject_html_dir, fn));
    if (fn.indexOf('.head.') >= 0) {
      inject_html_head.push(content);
    } else if (fn.indexOf('.body.') >= 0) {
      inject_html_body.push(content);
    } else {
      inject_html_end.push(content);
    }
  });
  if (filenames.length === 0) {
    console.log('no files to inject found in:', inject_html_dir);
  }
} else {
  console.log('no files to inject found as the directory does not exist:', inject_html_dir);
}

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
        API_URL: `'${API_URL}'`
      }
    }),
    new HtmlWebpackPlugin({
      template: './index.web.ejs',
      inject_html_head: inject_html_head.join('\n'),
      inject_html_body: inject_html_body.join('\n'),
      inject_html_end: inject_html_end.join('\n')
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

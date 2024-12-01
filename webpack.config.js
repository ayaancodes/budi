const path = require('path');

module.exports = {
    entry: './src/popup.js', // Entry point for the React component
    output: {
        path: path.resolve(__dirname, 'src'), // Output directory
        filename: 'popup.bundle.js' // Output file name
    },
    module: {
        rules: [
            {
                test: /\.jsx?$/, // Match both .js and .jsx files
                exclude: /node_modules/, // Exclude node_modules directory
                use: {
                    loader: 'babel-loader', // Use Babel loader for transpiling
                    options: {
                        presets: ['@babel/preset-react'] // Use React preset
                    }
                }
            }
        ]
    },
    resolve: {
        extensions: ['.js', '.jsx'] // Resolve these extensions
    }
};
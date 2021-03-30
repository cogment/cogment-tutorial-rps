import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import { App } from './App';
import { createMuiTheme, responsiveFontSizes, ThemeProvider } from '@material-ui/core/styles';

let theme = createMuiTheme({
    palette: {
        primary: {
            light: "#c5cce8",
            main: "#6B80C4",
        },
        secondary: {
            main: "#ffb400",
        },
    },
});

theme = responsiveFontSizes(theme);

ReactDOM.render(

    <React.StrictMode>
        <ThemeProvider theme={theme}>
            <App />
        </ThemeProvider>
    </React.StrictMode>,
    document.getElementById('root')
);

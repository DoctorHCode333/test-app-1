import React from 'react';
import {createRoot} from 'react-dom/client';
import Main from './main';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import './index.css';
import './App.css';
import {configureStore} from '@reduxjs/toolkit';
import rootReducer from './Redux/reducers';
import {Provider} from 'react-redux';
import 'primereact/resources/primereact.css';

import 'primereact/resources/themes/lara-light-indigo/theme.css';
  
   import 'primeicons/primeicons.css';
   import 'primeflex/primeflex.css';
const store = configureStore({reducer: rootReducer,
  middleware:(getDefaultMiddleware)=>getDefaultMiddleware({immutableCheck:false,
    serializableCheck:false,
  })
});
const theme = createTheme();

const root = createRoot(document.getElementById('root'))

root.render(
  <ThemeProvider theme={theme}>
    <Provider store={store}>
        <CssBaseline /> 
        <Main />
  </Provider>
  </ThemeProvider>
  
)

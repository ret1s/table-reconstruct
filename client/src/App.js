import React, { useState, useEffect } from 'react';
import Preloader from './components/Pre';
import WithSubnavigation from './components/Navbar';
import Home from './components/Home/Home';
import About from './components/About/About';
import Product from './components/Product/Product';
import Footer from './components/Footer';
import { ChakraProvider } from '@chakra-ui/react';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from 'react-router-dom';
import ScrollToTop from './components/ScrollToTop';
import './style.css';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';

function App() {
  const [load, upadateLoad] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      upadateLoad(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  return (
    <ChakraProvider>
      <Router>
        <Preloader load={load} />
        <div className="App" id={load ? 'no-scroll' : 'scroll'}>
          <WithSubnavigation />
          <ScrollToTop />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/product" element={<Product />} />
            <Route path="/about" element={<About />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
          <Footer className="footer"/>
        </div>
      </Router>
    </ChakraProvider>
  );
}

export default App;

import { BrowserRouter, Routes, Route} from 'react-router-dom';
import './App.css';
import Homepage from './pages/homepage';
import Product from './pages/product';
import About from './pages/about';
import SignIn from './pages/sign-in';
import NotFound from './pages/404'
import './autoload'

function App() {
  let DEFAULT_ROUTE_PAGE = <Homepage />;

  return (
    <BrowserRouter>
      <Routes>
        <Route index element={DEFAULT_ROUTE_PAGE} />
        <Route path='product' element={<Product />} />
        <Route path='about' element={<About />} />
        <Route path='sign-in' element={<SignIn />} />
        <Route path='*' element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;

import { BrowserRouter, Routes, Route} from 'react-router-dom';
import './App.css';
import Homepage from './pages/homepage';
import Product from './pages/product';
import About from './pages/about';
import SignIn from './pages/sign-in';
import SignOut from './pages/sign-out';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route index element={<Homepage />} />
        <Route path='product' element={<Product />} />
        <Route path='about' element={<About />} />
        <Route path='sign-in' element={<SignIn />} />
        <Route path='sign-out' element={<SignOut />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

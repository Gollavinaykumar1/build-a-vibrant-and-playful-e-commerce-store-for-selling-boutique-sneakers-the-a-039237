# LLM Output

=== FILE: src/App.jsx ===
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { HashRouter, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { login, register, getItems, createItem } from './api';
import { clsx } from 'clsx';

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [user, setUser] = useState(null);
  const [items, setItems] = useState([]);
  const [cart, setCart] = useState([]);
  const [isAdmin, setIsAdmin] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  const handleLogin = async (email, password) => {
    try {
      const response = await login(email, password);
      setUser(response.data);
      setIsAdmin(response.data.isAdmin);
    } catch (error) {
      console.error(error);
    }
  };

  const handleRegister = async (email, password) => {
    try {
      const response = await register(email, password);
      setUser(response.data);
      setIsAdmin(response.data.isAdmin);
    } catch (error) {
      console.error(error);
    }
  };

  const handleGetItems = async () => {
    try {
      const response = await getItems();
      const safeList = Array.isArray(response.data) ? response.data : (response.data?.items || []);
      setItems(safeList);
    } catch (error) {
      console.error(error);
    }
  };

  const handleCreateItem = async (name, price) => {
    try {
      const response = await createItem(name, price);
      setItems([...items, response.data]);
    } catch (error) {
      console.error(error);
    }
  };

  const handleAddToCart = (item) => {
    setCart([...cart, item]);
  };

  const handleRemoveFromCart = (item) => {
    setCart(cart.filter((i) => i.id !== item.id));
  };

  useEffect(() => {
    handleGetItems();
  }, []);

  const Header = () => {
    return (
      <div className="bg-pink-500 text-white p-4 flex justify-between">
        <h1 className="text-3xl font-bold">Sneaker Store</h1>
        {user ? (
          <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" onClick={() => setModalOpen(true)}>Add New Sneaker</button>
        ) : (
          <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" onClick={() => window.location.href = '/login'}>Login</button>
        )}
      </div>
    );
  };

  const Footer = () => {
    return (
      <div className="bg-gray-200 p-4 text-center">
        2023 Sneaker Store
      </div>
    );
  };

  const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (event) => {
      event.preventDefault();
      handleLogin(email, password);
    };

    return (
      <div className="max-w-md mx-auto p-4">
        <h2 className="text-2xl font-bold">Login</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">Email</label>
            <input className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">Password</label>
            <input className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </div>
          <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" type="submit">Login</button>
        </form>
      </div>
    );
  };

  const Register = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (event) => {
      event.preventDefault();
      handleRegister(email, password);
    };

    return (
      <div className="max-w-md mx-auto p-4">
        <h2 className="text-2xl font-bold">Register</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">Email</label>
            <input className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} />
          </div>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">Password</label>
            <input className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
          </div>
          <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" type="submit">Register</button>
        </form>
      </div>
    );
  };

  const Store = () => {
    return (
      <div className="max-w-5xl mx-auto p-4">
        <h2 className="text-2xl font-bold">Sneaker Store</h2>
        <div className="grid grid-cols-4 gap-4">
          {items.map((item) => (
            <div key={item.id} className="bg-white rounded shadow-md p-4">
              <h3 className="text-lg font-bold">{item.name}</h3>
              <p className="text-gray-700">${item.price}</p>
              <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" onClick={() => handleAddToCart(item)}>Add to Cart</button>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const Cart = () => {
    return (
      <div className="max-w-md mx-auto p-4">
        <h2 className="text-2xl font-bold">Cart</h2>
        <ul>
          {cart.map((item) => (
            <li key={item.id} className="py-2 border-b border-gray-200">
              <span className="text-lg font-bold">{item.name}</span>
              <span className="text-gray-700">${item.price}</span>
              <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" onClick={() => handleRemoveFromCart(item)}>Remove</button>
            </li>
          ))}
        </ul>
        <p className="text-lg font-bold">Total: ${cart.reduce((acc, item) => acc + item.price, 0)}</p>
      </div>
    );
  };

  const Modal = () => {
    const [name, setName] = useState('');
    const [price, setPrice] = useState('');

    const handleSubmit = (event) => {
      event.preventDefault();
      handleCreateItem(name, price);
      setModalOpen(false);
    };

    return (
      <div className={clsx('fixed top-0 left-0 w-full h-full bg-gray-500 bg-opacity-75 flex justify-center items-center', modalOpen ? 'block' : 'hidden')}>
        <div className="bg-white rounded shadow-md p-4">
          <h2 className="text-2xl font-bold">Add New Sneaker</h2>
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">Name</label>
              <input className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="name" type="text" value={name} onChange={(event) => setName(event.target.value)} />
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="price">Price</label>
              <input className="appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" id="price" type="number" value={price} onChange={(event) => setPrice(event.target.value)} />
            </div>
            <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" type="submit">Add</button>
          </form>
        </div>
      </div>
    );
  };

  return (
    <HashRouter>
      <Header />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/store" element={<Store />} />
        <Route path="/cart" element={<Cart />} />
      </Routes>
      <Footer />
      <Modal />
      <ToastContainer />
    </HashRouter>
  );
}

export default App;
=== END ===
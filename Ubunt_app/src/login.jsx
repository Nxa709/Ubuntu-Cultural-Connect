import "../../assets/css/main.css";
import "../../assets/css/login.css";
import React, { useState } from "react";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({ username, password, rememberMe });
  };

  return (
    <>
      <header id="header" className="header position-relative">
        <div className="container-fluid container-xl position-relative">
          <div className="top-row d-flex align-items-center justify-content-between">
            <a href="/" className="logo d-flex align-items-end">
              <img src="/img/Ubuntu_logo/Ubuntu-logo.png" alt="Company Logo" />
              <h1 className="sitename"></h1>
              <span></span>
            </a>

            <div className="d-flex align-items-center">
              <div className="social-links">
                <a href="#" className="facebook">
                  <i className="bi bi-facebook"></i>
                </a>
                <a href="#" className="twitter">
                  <i className="bi bi-twitter"></i>
                </a>
                <a href="#" className="instagram">
                  <i className="bi bi-instagram"></i>
                </a>
              </div>

              <form className="search-form ms-4">
                <input type="text" placeholder="Search..." className="form-control" />
                <button type="submit" className="btn">
                  <i className="bi bi-search"></i>
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="nav-wrap">
          <div className="container d-flex justify-content-center position-relative">
            <nav id="navmenu" className="navmenu">
              <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About Us</a></li>
                <li><a href="/contact">Contact</a></li>
                <li><a href="/register">Register</a></li>
                <li><a href="/login">Login</a></li>
                <li className="dropdown">
                  <a href="#">
                    <span>Pages</span>{" "}
                    <i className="bi bi-chevron-down toggle-dropdown"></i>
                  </a>
                  <ul>
                    <li><a href="/about">About Us</a></li>
                    <li><a href="/register">Register</a></li>
                    <li><a href="/login">Login</a></li>
                    <li><a href="/404">404 Not Found Page</a></li>
                    <li className="dropdown">
                      <a href="#">
                        <span>Deep Dropdown</span>{" "}
                        <i className="bi bi-chevron-down toggle-dropdown"></i>
                      </a>
                      <ul>
                        <li><a href="#">Deep Dropdown 1</a></li>
                        <li><a href="#">Deep Dropdown 2</a></li>
                        <li><a href="#">Deep Dropdown 3</a></li>
                        <li><a href="#">Deep Dropdown 4</a></li>
                        <li><a href="#">Deep Dropdown 5</a></li>
                      </ul>
                    </li>
                  </ul>
                </li>
              </ul>
              <i className="mobile-nav-toggle d-xl-none bi bi-list"></i>
            </nav>
          </div>
        </div>
      </header>

      <main className="main">
        <form className="login" onSubmit={handleSubmit}>
          <h1>Login to your Account</h1>
          <p>See what Africa is like</p>

          <button type="button" className="google-btn">
            <img
              src="https://developers.google.com/identity/images/g-logo.png"
              alt="Google logo"
            />
            Login with Google
          </button>

          <div className="divider">
            <span>OR SIGN IN WITH EMAIL</span>
          </div>

          <label htmlFor="username">Email/Username:</label>
          <br />
          <input
            id="username"
            className="input-modern"
            name="username"
            type="email"
            placeholder="e.g 1234@gmail.com"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />

          <label htmlFor="password">Password:</label>
          <br />
          <input
            id="password"
            className="input-modern"
            name="password"
            type="password"
            placeholder="******"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <div className="form-options">
            <label>
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />{" "}
              Remember me
            </label>

            <div className="errorMsg"></div>

            <a href="#">Forgot password?</a>
          </div>

          <input className="btn-modern" type="submit" value="Login" />
        </form>
      </main>
    </>
  );
}

export default Login;
import React from "react";

function Footer() {
  return (
    <footer id="footer" className="footer">

      <div className="container copyright text-center mt-4">
        <p>
          © <span>Copyright</span>{" "}
          <strong className="px-1 sitename">
            Ubuntu Cultural Connect
          </strong>{" "}
          <span>All Rights Reserved</span>
        </p>

        <div className="credits">
          Designed by{" "}
          <a href="https://bootstrapmade.com/">
            BootstrapMade
          </a>{" "}
          |{" "}
          <a href="https://bootstrapmade.com/tools/">
            DevTools
          </a>
        </div>
      </div>

    </footer>
  );
}

export default Footer;
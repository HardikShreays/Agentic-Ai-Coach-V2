import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";

function App() {
  const redirectUrl = import.meta.env.VITE_REDIRECT_URL;

  useEffect(() => {
    if (redirectUrl) {
      window.location.replace(redirectUrl);
    }
  }, [redirectUrl]);

  if (!redirectUrl) {
    return (
      <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
        <h2>Missing redirect URL</h2>
        <p>
          Set <code>VITE_REDIRECT_URL</code> in <code>frontend/.env</code>.
        </p>
      </main>
    );
  }

  return (
    <main style={{ fontFamily: "sans-serif", padding: "2rem" }}>
      <p>Redirecting to {redirectUrl} ...</p>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);

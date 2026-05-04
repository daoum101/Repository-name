import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import Landing from "@/pages/Landing";
import Dashboard from "@/pages/Dashboard";
import NewProject from "@/pages/NewProject";
import Editor from "@/pages/Editor";
import "@/App.css";

function App() {
  useEffect(() => {
    const saved = localStorage.getItem("autosite-theme") || "dark";
    document.documentElement.classList.toggle("dark", saved === "dark");
  }, []);

  return (
    <div className="App min-h-screen bg-background text-foreground grain">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/new" element={<NewProject />} />
          <Route path="/projects/:id" element={<Editor />} />
        </Routes>
      </BrowserRouter>
      <Toaster richColors theme="dark" position="bottom-right" />
    </div>
  );
}

export default App;

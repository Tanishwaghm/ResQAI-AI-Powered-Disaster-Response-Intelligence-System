
import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";

export default function App() {
  const [activeTab, setActiveTab] = useState("chat");
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main */}
      <main className="flex-1 overflow-hidden">
        <Home activeTab={activeTab} />
      </main>
    </div>
  );
}

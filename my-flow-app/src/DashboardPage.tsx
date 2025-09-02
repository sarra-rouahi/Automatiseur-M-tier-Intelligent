// src/components/Dashboard.tsx
import React from "react";
import { Outlet, Link } from "react-router-dom";
import { useAuth } from "../src/contexts/AuthContext";
import ReactFlow, { Background, MiniMap, Controls } from "reactflow";
import 'reactflow/dist/style.css';

const Dashboard: React.FC = () => {
  const { logout } = useAuth();

  // Exemple de nœuds pour React Flow
  const nodes = [
    { id: '1', type: 'input', data: { label: 'Email Node' }, position: { x: 0, y: 50 } },
    { id: '2', type: 'default', data: { label: 'OCR Node' }, position: { x: 250, y: 50 } },
    { id: '3', type: 'default', data: { label: 'Classification Node' }, position: { x: 500, y: 50 } },
    { id: '4', type: 'default', data: { label: 'Sentiment Node' }, position: { x: 750, y: 50 } },
    { id: '5', type: 'output', data: { label: 'Summary Node' }, position: { x: 1000, y: 50 } },
  ];

  const edges = [
    { id: 'e1-2', source: '1', target: '2' },
    { id: 'e2-3', source: '2', target: '3' },
    { id: 'e3-4', source: '3', target: '4' },
    { id: 'e4-5', source: '4', target: '5' },
  ];

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 text-white flex flex-col">
        <div className="p-6 text-xl font-bold">LCNC Dashboard</div>
        <nav className="flex-1">
          <ul>
            <li className="p-4 hover:bg-gray-700"><Link to="/dashboard">Home</Link></li>
            <li className="p-4 hover:bg-gray-700"><Link to="/workflows">Workflows</Link></li>
            <li className="p-4 hover:bg-gray-700"><Link to="/profile">Profile</Link></li>
          </ul>
        </nav>
        <button 
          onClick={logout} 
          className="m-6 p-2 bg-red-600 rounded hover:bg-red-700">
          Logout
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 bg-gray-100 p-4 overflow-auto">
        <h1 className="text-2xl font-bold mb-4">Workflow Editor</h1>

        <div className="w-full h-[600px] bg-white rounded shadow">
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background />
            <MiniMap />
            <Controls />
          </ReactFlow>
        </div>

        <Outlet /> {/* Pour les routes enfants */}
      </main>
    </div>
  );
};

export default Dashboard;

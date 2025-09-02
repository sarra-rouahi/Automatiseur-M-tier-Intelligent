import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import OAuthButtons from "./OAuthButtons";

const LoginForm: React.FC = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      window.location.href = "/dashboard";
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erreur lors du login");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-indigo-500 to-blue-400 p-4">
  <div className="auth-container bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
    <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">Connexion</h2>

    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
        className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <input
        type="password"
        placeholder="Mot de passe"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
        className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <button
        type="submit"
        className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition duration-300"
      >
        Se connecter
      </button>
    </form>

    <div  className="separator">ou</div>

    <OAuthButtons />

    <p className="text-center mt-6 text-gray-600">
      Pas encore de compte ?{" "}
      <a href="/signup" className="text-indigo-600 font-semibold hover:underline">
        S'inscrire
      </a>
    </p>
  </div>
</div>

  );
};

export default LoginForm;

// src/pages/Dashboard.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { userApi } from "../api/userApi";
import { emailApi } from "../api/emailApi";
import { useAuth } from "../contexts/AuthContext";

const Dashboard = () => {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  // Profil utilisateur
  const [profile, setProfile] = useState<any>(null);
  const [editProfile, setEditProfile] = useState({ username: "", email: "" });

  // Emails
  const [emails, setEmails] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  // Charger infos utilisateur et emails
  useEffect(() => {
    console.log("User context:", user);
    if (user?.id) {
      fetchUser(user.id);
      fetchInbox();
    }
  }, [user]);

  // Récupération profil utilisateur
  const fetchUser = async (id: string) => {
    try {
      const res = await userApi.getById(id);
      console.log("fetchUser response:", res);

      const data = res.data || res; // gérer les deux cas
      if (!data) {
        console.error("Aucune donnée reçue pour l'utilisateur");
        return;
      }

      setProfile(data);
      setEditProfile({ username: data.username, email: data.email });
    } catch (error) {
      console.error("Erreur profil:", error);
      alert("Impossible de charger le profil");
    }
  };

  // Récupération des emails de la boîte mail
  const fetchInbox = async () => {
    setLoading(true);
    try {
      const res = await emailApi.getAll();
      const data = res.data || res; // gérer les deux cas
      setEmails(data);
      console.log("Emails reçus:", data);
    } catch (error) {
      console.error("Erreur chargement emails:", error);
      alert("Impossible de charger les emails");
    } finally {
      setLoading(false);
    }
  };

  // Supprimer un email
  const handleDelete = async (id: string) => {
    try {
      await emailApi.delete(id);
      setEmails((prev) => prev.filter((email) => email.id !== id));
    } catch (error) {
      console.error("Erreur suppression email:", error);
      alert("Impossible de supprimer l'email");
    }
  };

  return (
    <div className="p-8 space-y-10">
      <h1 className="text-3xl font-bold">📊 Tableau de bord</h1>

      {/* Profil utilisateur */}
      <section className="p-6 border rounded-lg bg-gray-50 shadow-sm">
        <h2 className="text-xl font-semibold mb-4">👤 Mon Profil</h2>
        {profile ? (
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              if (!user?.id) return;
              try {
                await userApi.update(user.id, editProfile);
                alert("Profil mis à jour ✅");
                fetchUser(user.id); // refresh
              } catch (err) {
                console.error(err);
                alert("Erreur mise à jour du profil");
              }
            }}
            className="space-y-3"
          >
            <input
              type="text"
              value={editProfile.username}
              onChange={(e) =>
                setEditProfile({ ...editProfile, username: e.target.value })
              }
              className="w-full p-2 border rounded-lg"
            />
            <input
              type="email"
              value={editProfile.email}
              onChange={(e) =>
                setEditProfile({ ...editProfile, email: e.target.value })
              }
              className="w-full p-2 border rounded-lg"
            />
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
            >
              Sauvegarder
            </button>
          </form>
        ) : (
          <p>Chargement du profil...</p>
        )}
      </section>

      {/* Emails */}
      <section className="p-6 border rounded-lg bg-gray-50 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">📩 Ma boîte mail</h2>
          <button
            onClick={fetchInbox}
            className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            🔄 Rafraîchir
          </button>
        </div>

        {loading ? (
          <p>Chargement...</p>
        ) : emails.length === 0 ? (
          <p>Aucun email trouvé.</p>
        ) : (
          <ul className="space-y-3">
            {emails.map((email) => (
              <li
                key={email.id}
                className="flex justify-between items-start border p-3 rounded-lg bg-white shadow-sm"
              >
                <div>
                  <p className="font-semibold">{email.subject || "(Sans objet)"}</p>
                  <p className="text-sm text-gray-600">
                    De: {email.sender} | {new Date(email.date).toLocaleString()}
                  </p>
                  <p className="text-sm">{email.body?.slice(0, 80)}...</p>
                </div>
                <button
                  onClick={() => handleDelete(email.id)}
                  className="px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600"
                >
                  Supprimer
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Navigation */}
      <div className="flex gap-4">
        <button
          onClick={() => navigate("/workflow")}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          🚀 Accéder au Workflow
        </button>
        <button
          onClick={logout}
          className="px-6 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800"
        >
          🔓 Déconnexion
        </button>
      </div>
    </div>
  );
};

export default Dashboard;

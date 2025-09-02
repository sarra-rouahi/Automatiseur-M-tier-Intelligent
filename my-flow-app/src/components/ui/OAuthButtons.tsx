import { useEffect } from "react";
import { authApi } from "../../api/authApi";

declare global {
  interface Window {
    google: any;
  }
}

const OAuthButtons: React.FC = () => {
  useEffect(() => {
    /* Initialisation Google */
    window.google.accounts.id.initialize({
      client_id: "77421909148-sq34np0rjuvf50p1k3o9j1qh55htc6pm.apps.googleusercontent.com", // ton Client ID
      callback: handleCredentialResponse,
    });

    /* Affichage du bouton Google */
    window.google.accounts.id.renderButton(
      document.getElementById("googleButton"),
      { theme: "outline", size: "large" }
    );
  }, []);

  const handleCredentialResponse = async (response: any) => {
    const id_token = response.credential; // <-- vrai token JWT
    try {
      const { data } = await authApi.loginGoogle({ id_token });
      localStorage.setItem("token", data.access_token);
      window.location.href = "/dashboard";
    } catch (error: any) {
      alert(error.response?.data?.detail || "Erreur login Google");
    }
  };

  return (
    <div className="oauth-buttons">
      <div id="googleButton"></div> {/* le bouton sera généré ici */}
    </div>
  );
};

export default OAuthButtons;

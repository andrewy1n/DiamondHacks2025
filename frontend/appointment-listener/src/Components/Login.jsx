import { useAuth0 } from "@auth0/auth0-react";

const LoginButton = () => {
  const { loginWithRedirect } = useAuth0();

  return (
    <button
      onClick={() =>
        loginWithRedirect({
          appState: { returnTo: "/home" },
          authorizationParams: {
            redirect_uri: `${window.location.origin}/auth/callback`,
          },
        })
      }
    >
      Log In
    </button>
  );
};

export default LoginButton;
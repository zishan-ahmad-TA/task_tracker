import styles from "./Login.module.css";

const Login = () => {
  const handleGoogleSignIn = () => {
    window.location.href = `${import.meta.env.VITE_BACKEND_URL}/login`;
  };

  return (
    <div className={styles.LoginPage}>
      <div className={styles.LoginContainer}>
        <h2 className={styles.Heading}>Welcome Back!</h2>
        <p className={styles.Description}>
          Your tasks, your way. Stay organized, stay on track. Let’s dive into
          your productivity journey.
        </p>
        <p className={styles.Subheading}>Sign in to continue</p>

        <button className={styles.GoogleSSOButton} onClick={handleGoogleSignIn}>
          Sign In with Google
        </button>

        <p className={styles.FooterText}>
          Made with ❤️ by the team at Tiger Analytics.
        </p>
      </div>
    </div>
  );
};

export default Login;

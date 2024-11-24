import styles from "./Login.module.css";

const Login = () => {
  const handleGoogleSignIn = () => {
    window.location.href = `${import.meta.env.VITE_BACKEND_URL}/login`;
  };

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginContainer}>
        <h2 className={styles.heading}>Welcome Back!</h2>
        <p className={styles.description}>
          Your tasks, your way. Stay organized, stay on track. Let’s dive into
          your productivity journey.
        </p>
        <p className={styles.subheading}>Sign in to continue</p>

        <button className={styles.googleSSOButton} onClick={handleGoogleSignIn}>
          Sign In with Google
        </button>

        <p className={styles.footerText}>
          Made with ❤️ by the team at Tiger Analytics.
        </p>
      </div>
    </div>
  );
};

export default Login;

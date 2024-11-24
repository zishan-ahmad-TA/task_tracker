import HoverCardComponent from "../ui-elements/HoverCard";
import styles from "./Navbar.module.css";

const Navbar = ({ navTitle, navDesc, profileImage, name, email, role }) => {

    return (
        <div className={styles.NavbarContainer}>
            <div className={styles.NavText}>
                <h2 className={styles.NavTitle}>
                    {navTitle}
                </h2>
                <p className={styles.NavDesc}>
                    {navDesc}
                </p>
            </div>

            <div className={styles.AvatarContainer}>
                <HoverCardComponent name={name} email={email} role={role} profileImage={profileImage} />
            </div>
        </div>
    );
};

export default Navbar;

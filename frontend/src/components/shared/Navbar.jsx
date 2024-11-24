import HoverCardComponent from "../ui-elements/HoverCard";
import styles from "./Navbar.module.css";

const Navbar = ({ navTitle, profileImage, name, email, role }) => {

    return (
        <div className={styles.NavbarContainer}>
            <h2 className={styles.NavTitle}>
                {navTitle}
            </h2>
            <div className={styles.AvatarContainer}>
                <HoverCardComponent name={name} email={email} role={role} profileImage={profileImage} />
            </div>
        </div>
    );
};

export default Navbar;

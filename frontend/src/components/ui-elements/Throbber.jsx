import styles from './Throbber.module.css';

const Throbber = () => {
    return (
        <div className={styles.throbberContainer}>
            <div className={styles.throbber}></div>
        </div>
    )
}

export default Throbber;
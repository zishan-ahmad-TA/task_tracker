import styles from './Input.module.css';

const Input = ({ label }) => {
    return (
        <fieldset className={styles.Fieldset}>
            <label className={styles.Label} htmlFor="project_name">
                {label}
            </label>
            <input className={styles.Input} id="project_name" />
        </fieldset>
    )
}

export default Input;
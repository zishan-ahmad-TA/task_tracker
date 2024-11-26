import styles from './Input.module.css';

const Input = ({ label, id, value, onChange, type = 'text' }) => {
    return (
        <fieldset className={styles.Fieldset}>
            <label className={styles.Label} htmlFor={id}>
                {label}
            </label>
            <input
                className={styles.Input}
                id={id}
                type={type}
                value={value}
                onChange={onChange}
            />
        </fieldset>
    );
};

export default Input;

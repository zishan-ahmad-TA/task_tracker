import Input from "../ui-elements/Input";
import MultiSelect from "../ui-elements/MultiSelect";
import styles from './CreateProjectForm.module.css';

const CreateProjectForm = () => {
    return (
        <div className={styles.CreateForm}>
            <Input label="Project Name" id="project_name" />
            <Input label="Project Description" id="project_description" />
            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="managers">
                    Managers
                </label>
                <MultiSelect id="managers" />
            </fieldset>
            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="employees">
                    Employees
                </label>
                <MultiSelect id="employees" />
            </fieldset>
        </div>
    );
}

export default CreateProjectForm;

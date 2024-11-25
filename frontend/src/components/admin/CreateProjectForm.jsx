import Input from "../ui-elements/Input";
import { DatePicker } from 'rsuite';
import 'rsuite/dist/rsuite.min.css';
import MultiSelect from "../ui-elements/MultiSelect";
import styles from './CreateProjectForm.module.css';

const CreateProjectForm = ({ members, managers }) => {

    const selectableMembers = members.map(member => ({
        value: member.employee_id,
        label: member.name,
    }));

    const selectableManagers = managers.map(manager => ({
        value: manager.employee_id,
        label: manager.name,
    }));
    return (
        <div className={styles.CreateForm}>
            <Input label="Project Name" id="project_name" />
            <Input label="Project Desc" id="project_description" />

            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="start_date">
                    Start Date
                </label>
                <DatePicker
                    oneTap
                    placeholder="Select Date"
                    style={{ width: '70%' }}
                    className={styles.DatePicker}
                />

            </fieldset>

            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="end_date">
                    End Date
                </label>
                <DatePicker
                    oneTap
                    placeholder="Select Date"
                    style={{ width: '70%' }}
                    className={styles.DatePicker}
                />

            </fieldset>

            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="managers">
                    Managers
                </label>
                <MultiSelect options={selectableManagers} id="managers" />
            </fieldset>
            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="employees">
                    Employees
                </label>
                <MultiSelect id="employees" options={selectableMembers} />
            </fieldset>
        </div>
    );
}

export default CreateProjectForm;


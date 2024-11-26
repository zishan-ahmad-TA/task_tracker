import Input from "../ui-elements/Input";
import { DatePicker } from 'rsuite';
import 'rsuite/dist/rsuite.min.css';
import MultiSelect from "../ui-elements/MultiSelect";
import styles from './ProjectForm.module.css';

const ProjectForm = ({ members, managers, formData, onInputChange }) => {

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
            <Input
                label="Project Name"
                id="project_name"
                value={formData.project_name}
                onChange={e => onInputChange('project_name', e.target.value)}
            />
            <Input
                label="Project Desc"
                id="project_description"
                value={formData.description}
                onChange={e => onInputChange('description', e.target.value)}
            />

            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="start_date">
                    Start Date
                </label>
                <DatePicker
                    oneTap
                    placeholder="Select Date"
                    style={{ width: '70%' }}
                    className={styles.DatePicker}
                    value={formData.start_date}
                    onChange={value => onInputChange('start_date', value)}
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
                    value={formData.end_date}
                    onChange={value => onInputChange('end_date', value)}
                />
            </fieldset>

            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="managers">
                    Managers
                </label>
                <MultiSelect
                    options={selectableManagers}
                    id="managers"
                    value={formData.managers}
                    onChange={value => onInputChange('managers', value)}
                />
            </fieldset>
            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="employees">
                    Employees
                </label>
                <MultiSelect
                    id="employees"
                    options={selectableMembers}
                    value={formData.employees}
                    onChange={value => onInputChange('employees', value)}
                />
            </fieldset>
        </div>
    );
};

export default ProjectForm;

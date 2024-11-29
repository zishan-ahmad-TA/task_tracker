import Input from "../ui-elements/Input";
import { DatePicker } from 'rsuite';
import 'rsuite/dist/rsuite.min.css';
import MultiSelect from "../ui-elements/MultiSelect";
import styles from '../admin/ProjectForm.module.css';

const TaskForm = ({ members, formData, onInputChange }) => {

    const selectableMembers = members.map(member => ({
        value: member.employee_id,
        label: member.name,
    }));


    return (
        <div className={styles.CreateForm}>
            <Input
                label="Task Name"
                id="task_name"
                value={formData.name}
                onChange={e => onInputChange('name', e.target.value)}
            />
            <Input
                label="Task Desc"
                id="task_description"
                value={formData.description}
                onChange={e => onInputChange('description', e.target.value)}
            />

            <fieldset className={styles.Fieldset}>
                <label className={styles.Label} htmlFor="due_date">
                    Due Date
                </label>
                <DatePicker
                    oneTap
                    placeholder="Select Date"
                    style={{ width: '70%' }}
                    className={styles.DatePicker}
                    value={formData.due_date}
                    onChange={value => onInputChange('due_date', value)}
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

export default TaskForm;

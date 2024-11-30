import StaticSelect from "../ui-elements/StaticSelect";
import styles from "../admin/ChangeRoles.module.css";

const ChangeTaskStatus = ({ formData, onInputChange }) => {

  const statuses = [
    { value: 'Not Started', label: 'Not Started' },
    { value: 'In Progress', label: 'In Progress' },
    { value: 'Completed', label: 'Completed'}
  ];

  return (
    <div className={styles.ChangeRoles}>
      {/* <fieldset className={styles.Fieldset}>
        <label className={styles.Label} htmlFor="employees">
          Employees
        </label>
        <StaticSelect
          id="employees"
          options={selectableEmployees}
          value={formData.employee}
          onChange={value => onInputChange('employee', value)}
        />
      </fieldset> */}

      <fieldset className={styles.Fieldset}>
        <label className={styles.Label} htmlFor="statuses">
          Status
        </label>
        <StaticSelect
          id="staus"
          options={statuses}
          value={formData.status}
          onChange={value => onInputChange('status', value)}
        />
      </fieldset>
    </div>
  );
}

export default ChangeTaskStatus;

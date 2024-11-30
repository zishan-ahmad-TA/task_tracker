import StaticSelect from "../ui-elements/StaticSelect";
import styles from "./ChangeRoles.module.css";

const ChangeRoles = ({ employees, formData, onInputChange }) => {
  const selectableEmployees = employees.map(employee => ({
    value: employee.employee_id,
    label: employee.name,
  }));

  const roles = [
    { value: 'manager', label: 'Manager' },
    { value: 'member', label: 'Member' },
  ];
 
  return (
    <div className={styles.ChangeRoles}>
      <fieldset className={styles.Fieldset}>
        <label className={styles.Label} htmlFor="employees">
          Employees
        </label>
        <StaticSelect
          id="employees"
          options={selectableEmployees}
          value={formData.employee}
          onChange={value => onInputChange('employee', value)}
        />
      </fieldset>

      <fieldset className={styles.Fieldset}>
        <label className={styles.Label} htmlFor="roles">
          Role
        </label>
        <StaticSelect
          id="roles"
          options={roles}
          value={formData.role}
          onChange={value => onInputChange('role', value)}
        />
      </fieldset>
    </div>
  );
}

export default ChangeRoles;

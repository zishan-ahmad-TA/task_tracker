import styles from '../admin/TeamCard.module.css';
import ListCard from '../shared/ListCard';
const TeamCard = ({ employeeData = [] }) => {
    return (
        <div className={styles.TeamContainer}>
            {employeeData.map((employee) => (
                <ListCard
                    key={employee.employee_id}
                    label={employee.name}
                    value={employee.email_id}
                    status={employee.role.charAt(0).toUpperCase() + employee.role.slice(1)}
                    showStatusIcon={false}
                    isWorkItems={false}
                />
            ))}
        </div>
    )
}

export default TeamCard;
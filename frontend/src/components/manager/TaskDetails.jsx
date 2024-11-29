import styles from "../shared/ProjectDetails.module.css";

const TaskDetails = ({ task }) => {
    if (!task) return <p>No task details available.</p>;

    return (
        <div>
            <h2 className={styles.projectTitle}>{task.name}</h2>
            <p className={styles.projectDescription}>{task.description || "No description provided"}</p>

            <div className={styles.detailsRow}>
                <div className={styles.detailItem}>
                    <strong>Status:</strong> {task.status || "Unknown"}
                </div>
            </div>

            <div className={styles.detailsRow}>
                <div className={styles.detailItem}>
                    <strong>Owner:</strong> {task.task_owner_name || "No owner specified"}
                </div>
            </div>

            <div className={styles.detailsRow}>
                <div className={styles.detailItem}>
                    <strong>Due Date:</strong>{" "}
                    {task.due_date ? new Date(task.due_date).toLocaleDateString() : "N/A"}
                </div>
            </div>

            <div className={styles.detailsSection}>
                <h3 className={styles.sectionTitle}>Team Members</h3>
                <p>
                    {task.members?.length
                        ? task.members.map(member => member.name).join(", ")
                        : "No team members assigned"}
                </p>
            </div>
        </div>
    );
};

export default TaskDetails;

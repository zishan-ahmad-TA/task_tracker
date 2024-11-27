import styles from "./ProjectDetails.module.css";

const ProjectDetails = ({ project }) => {
    if (!project) return <p>No project details available.</p>;

    return (
        <div>
            <h2 className={styles.projectTitle}>{project.project_name}</h2>
            <p className={styles.projectDescription}>{project.description || "No description provided"}</p>

            <div className={styles.detailsRow}>
                <div className={styles.detailItem}>
                    <strong>Status:</strong> {project.project_status || "Unknown"}
                </div>
                <div className={styles.detailItem}>
                    <strong>Owner:</strong> {project.project_owner_name || "No owner specified"}
                </div>
            </div>

            <div className={styles.detailsRow}>
                <div className={styles.detailItem}>
                    <strong>Start Date:</strong>{" "}
                    {project.start_date ? new Date(project.start_date).toLocaleDateString() : "N/A"}
                </div>
                <div className={styles.detailItem}>
                    <strong>End Date:</strong>{" "}
                    {project.end_date ? new Date(project.end_date).toLocaleDateString() : "N/A"}
                </div>
            </div>

            <div className={styles.detailsSection}>
                <h3 className={styles.sectionTitle}>Managers</h3>
                <p>
                    {project.managers?.length
                        ? project.managers.map(manager => manager.name).join(", ")
                        : "No managers assigned"}
                </p>
            </div>

            <div className={styles.detailsSection}>
                <h3 className={styles.sectionTitle}>Team Members</h3>
                <p>
                    {project.members?.length
                        ? project.members.map(member => member.name).join(", ")
                        : "No team members assigned"}
                </p>
            </div>
        </div>
    );
};

export default ProjectDetails;

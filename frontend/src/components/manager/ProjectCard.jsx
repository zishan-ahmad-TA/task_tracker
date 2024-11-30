import styles from '../admin/ProjectCard.module.css';
import ListCard from '../shared/ListCard';
import DialogComponent from '../ui-elements/Dialog';
import ToastComponent from '../ui-elements/Toast';
import useApiRequest from '../../hooks/apiRequest';
import { useState } from 'react';

const ProjectCard = ({ projects, onViewClick }) => {

    const apiRequest = useApiRequest();

    const [toastMessage, setToastMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [isToastOpen, setIsToastOpen] = useState(false);

    return (
        <>
            <ToastComponent
                open={isToastOpen}
                setOpen={setIsToastOpen}
                toastMessage={toastMessage}
                toastTitle={isError ? "Error Occurred ❌" : "All Set! ✅"}
            />

            <div className={styles.ProjectContainer}>
                <div className={styles.ListTitle}>Projects</div>

                {projects.length === 0 ? (
                    <div className={styles.NoProjects}>No Projects Found</div>
                ) : (
                    projects.map((project, index) => (
                        <ListCard
                            key={index}
                            label={project.project_name}
                            value={project.description}
                            status={project.project_status}
                            listClickable={true}
                            onLabelClick={() => onViewClick(project.project_id)}
                            isWorkItems={false}
                        />
                    ))
                )}
            </div>
        </>
    );
};

export default ProjectCard;

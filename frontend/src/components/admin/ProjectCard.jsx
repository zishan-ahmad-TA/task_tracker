import styles from '../admin/ProjectCard.module.css';
import ListCard from '../shared/ListCard';
import DialogComponent from '../ui-elements/Dialog';
import apiRequest from '../../utils/apiRequest';
import ToastComponent from '../ui-elements/Toast';
import { useState } from 'react';

const ProjectCard = ({ projects, fetchProjects }) => {

    const [isDeleteProjectModalOpen, setIsDeleteProjectModalOpen] = useState(false);
    const [projectIdToDelete, setProjectIdToDelete] = useState(null);
    const [toastMessage, setToastMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [isToastOpen, setIsToastOpen] = useState(false);
    const closeDeleteProject = () => {
        setIsDeleteProjectModalOpen(false);
    }

    const deleteProjects = async (projectId) => {
        if (!projectId) return;
        try {
            const url = `/projects/${projectId}`;
            await apiRequest(url, 'DELETE');
            setIsError(false);
            setToastMessage("The project was deleted successfully!");
            setIsToastOpen(true);
            await fetchProjects();
            setProjectIdToDelete(null);
        }

        catch (error) {
            setToastMessage("Failed to delete project");
            setIsError(true);
            setIsToastOpen(true);
            console.error(error);
        }

    };

    return (
        <>
            <DialogComponent open={isDeleteProjectModalOpen}
                onOpenChange={closeDeleteProject}
                title="Delete project"
                description="Are you sure you want to delete this project?"
                buttonText="Delete"
                buttonColor="#ff4d3d"
                onSubmit={() => deleteProjects(projectIdToDelete)} />

            <ToastComponent
                open={isToastOpen}
                setOpen={setIsToastOpen}
                toastMessage={toastMessage}
                toastTitle={isError ? "Error Occurred ❌" : "All Set! ✅"}
            />
            <div className={styles.ProjectContainer}>
                {projects.map((project, index) => (
                    <ListCard
                        key={index}
                        label={project.project_name}
                        value={project.description}
                        status={project.project_status}
                        onDeleteIconClick={() => {
                            setIsDeleteProjectModalOpen(true);
                            setProjectIdToDelete(project.project_id);
                        }}
                    />
                ))}
            </div>

        </>
    );
};


export default ProjectCard;
import styles from '../admin/ProjectCard.module.css';
import ListCard from '../shared/ListCard';
import DialogComponent from '../ui-elements/Dialog';
import apiRequest from '../../utils/apiRequest';
import { useState } from 'react';

const ProjectCard = ({ projects, setProjects }) => {

    const [isDeleteProjectModalOpen, setIsDeleteProjectModalOpen] = useState(false);
    const [projectIdToDelete, setProjectIdToDelete] = useState(null);
    const closeDeleteProject = () => {
        setIsDeleteProjectModalOpen(false);
    }

    const deleteProjects = async (projectId) => {
        if (!projectId) return;
        try {
            const url = `${import.meta.env.VITE_BACKEND_URL}/projects/${projectId}`;
            await apiRequest(url, 'DELETE');
            setProjects((prevProjects) => prevProjects.filter((item) => item.project_id !== projectId))
            setProjectIdToDelete(null);
        }

        catch (error) {
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
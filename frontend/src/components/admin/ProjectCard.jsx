import styles from '../admin/ProjectCard.module.css';
import ListCard from '../shared/ListCard';
import DialogComponent from '../ui-elements/Dialog';
import { useState } from 'react';

const ProjectCard = ({ projects }) => {

    const [isDeleteProjectModalOpen, setIsDeleteProjectModalOpen] = useState(false);
    const closeDeleteProject = () => {
        setIsDeleteProjectModalOpen(false);
    }

    return (
        <>
            <DialogComponent open={isDeleteProjectModalOpen}
                onOpenChange={closeDeleteProject}
                title="Delete project"
                description="Are you sure you want to delete this project?"
                buttonText="Delete"
                buttonColor="#ff4d3d" />


            <div className={styles.ProjectContainer}>
                {projects.map((project, index) => (
                    <ListCard
                        key={index}
                        label={project.project_name}
                        value={project.description}
                        status={project.project_status}
                        onDeleteIconClick={() => setIsDeleteProjectModalOpen(true)}
                    />
                ))}
            </div>
        </>
    );
};


export default ProjectCard;
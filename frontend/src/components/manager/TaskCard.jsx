import styles from '../admin/ProjectCard.module.css';
import ListCard from '../shared/ListCard';
import DialogComponent from '../ui-elements/Dialog';
import ToastComponent from '../ui-elements/Toast';
import useApiRequest from '../../hooks/apiRequest';
import { useState } from 'react';

const TaskCard = ({ tasks, projectId, fetchTasks, onEditClick, onViewClick, user , del}) => {

    const apiRequest = useApiRequest();
    const [isDeleteTaskModalOpen, setIsDeleteTaskModalOpen] = useState(false);
    const [taskIdToDelete, setTaskIdToDelete] = useState(null);
    const [toastMessage, setToastMessage] = useState('');
    const [isError, setIsError] = useState(false);
    const [isToastOpen, setIsToastOpen] = useState(false);

    const closeDeleteTask = () => {
        setIsDeleteTaskModalOpen(false);
    }

    const deleteTasks = async (taskId) => {
        if (!taskId) return;
        try {
            const url = `/tasks/${taskId}`;
            await apiRequest(url, 'DELETE');
            setIsError(false);
            setToastMessage("The task was deleted successfully!");
            setIsToastOpen(true);
            if(!user)
                await fetchTasks(projectId);
            else
                await fetchTasks(projectId, user.employee_id)
            setTaskIdToDelete(null);
        }

        catch (error) {
            setToastMessage("Failed to delete task");
            setIsError(true);
            setIsToastOpen(true);
            console.error(error);
        }

    };

    return (
        <>
            <DialogComponent open={isDeleteTaskModalOpen}
                onOpenChange={closeDeleteTask}
                title="Delete task"
                description="Are you sure you want to delete this task?"
                buttonText="Delete"
                buttonColor="#ff4d3d"
                onSubmit={() => deleteTasks(taskIdToDelete)} 
            />

            <ToastComponent
                open={isToastOpen}
                setOpen={setIsToastOpen}
                toastMessage={toastMessage}
                toastTitle={isError ? "Error Occurred ❌" : "All Set! ✅"}
            />

            <div className={styles.ProjectContainer}>
                <div className = {styles.ListTitle}>Tasks</div>
                {tasks.map((task, index) => (
                    <ListCard
                        key={index}
                        label={task.name}
                        value={task.description}
                        status={task.status}
                        onDeleteIconClick={() => {
                            setIsDeleteTaskModalOpen(true);
                            setTaskIdToDelete(task.task_id);
                        }}

                        isDelete = {del}

                        onEditIconClick={() => {
                            onEditClick(task.task_id);
                        }}
                        listClickable={true}
                        onLabelClick={() => onViewClick(task.task_id)}
                    />
                ))}
            </div>

        </>
    );
};


export default TaskCard;
import { useEffect, useState } from "react";
import ToastComponent from "../components/ui-elements/Toast";
import styles from './AdminPage.module.css';
import Navbar from '../components/shared/Navbar';
import KpiCard from "../components/shared/KpiCard";
import ProjectCard from "../components/manager/ProjectCard";
import TaskCard from "../components/manager/TaskCard"
import DialogComponent from "../components/ui-elements/Dialog";
import useApiRequest from "../hooks/apiRequest";
import TaskForm from "../components/manager/TaskForm";
import Loader from "../components/ui-elements/Loader";
import TaskDetails from "../components/manager/TaskDetails";


import { VscFileSymlinkDirectory } from "react-icons/vsc";
import { FaUsers } from "react-icons/fa";



const ManagerPage = ({ userDetails }) => {
  const apiRequest = useApiRequest();
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [tasks, setTasks] = useState([]);
  const [totalProjects, setTotalProjects] = useState('NA');
  const [totalTasks, setTotalTasks] = useState('NA');
  const [employees, setEmployees] = useState([]);
  const [members, setMembers] = useState([]);
  const [isAddTaskModalOpen, setIsAddTaskModalOpen] = useState(false);
  const [isEditTaskModalOpen, setIsEditTaskModalOpen] = useState(false);
  const [isViewTaskModalOpen, setIsViewTaskModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedEditTask, setSelectedEditTask] = useState(null);
  const [toastMessage, setToastMessage] = useState('');
  const [isToastOpen, setIsToastOpen] = useState(false);
  const [isError, setIsError] = useState(false);

  const [taskCreateData, setTaskCreateData] = useState({
    name: '',
    description: '',
    due_date: null,
    employees: [],
  });

  const [taskEditData, setTaskEditData] = useState({
    name: '',
    description: '',
    due_date: null,
    employees: [],
  });

  const closeAddTask = () => {
    setTaskCreateData({
      name: '',
      description: '',
      due_date: null,
      employees: [],
    });
    setIsAddTaskModalOpen(false);
  };

  const closeEditTask = () => {
    setTaskEditData({
      name: '',
      description: '',
      due_date: null,
      employees: [],
    });
    setIsEditTaskModalOpen(false);
    setSelectedEditTask(null);
  };

  const closeViewTask = () => {
    setSelectedTask(null);
    setIsViewTaskModalOpen(false);
  };

  const handleTaskInput = (key, value) => {
    setTaskCreateData(prevState => ({
      ...prevState,
      [key]: value,
    }));
  };

  const handleEditInput = (key, value) => {
    setTaskEditData(prevState => ({
      ...prevState,
      [key]: value,
    }));
  };

  const handleCreateTask = async (projectId) => {
    const payload = {
      name: taskCreateData.name,
      description: taskCreateData.description,
      due_date: taskCreateData.due_date ? taskCreateData.due_date.toISOString() : null,
      employee_ids: taskCreateData.employees.map(employee => employee.value),
    };

    try {
      await apiRequest(`/tasks/${projectId}`, 'POST', payload);
      closeAddTask();
      setIsError(false);
      setToastMessage("Success! Your new task has been created!");
      setIsToastOpen(true);
      await fetchTasks(projectId);

    } catch (error) {
      setIsError(true);
      setToastMessage("Failed to create task");
      setIsToastOpen(true);
      console.error(error.message);
    }
  };

  const handleViewTasks = async (projectId) => {
    if(!projectId) return;
    try {
      const projectDetailData = await apiRequest(`/projects/${projectId}`);
      setSelectedProject(projectDetailData);
    } 
    
    catch (error) {
      console.error("Error fetching task details:", error);
      setIsError(true);
      setToastMessage("Failed to fetch task details");
      setIsToastOpen(true);
    }
  };

  const handleEditTask = async () => {
    const payload = {
      name: taskEditData.name,
      description: taskEditData.description,
      due_date: taskEditData.due_date ? taskEditData.due_date.toISOString() : null,
      employee_ids: taskEditData.employees.map(employee => employee.value),
    };

    try {
      await apiRequest(`/tasks/${selectedEditTask}`, 'PUT', payload);
      closeAddTask();
      setIsError(false);
      setToastMessage("Success! Your task has been edited!");
      setIsToastOpen(true);
      await fetchTasks(selectedProject.project_id);

    } catch (error) {
      setIsError(true);
      setToastMessage("Failed to edit task");
      setIsToastOpen(true);
      console.error(error.message);
    }
  };

  const openEditTask = async (taskId) => {
    try {
      setIsEditTaskModalOpen(true);
      const taskDetailData = await apiRequest(`/tasks/${taskId}`);
      setSelectedEditTask(taskDetailData.task_id)

      setTaskEditData({
        name: taskDetailData.name,
        description: taskDetailData.description,
        due_date: new Date(taskDetailData.due_date),
        employees: taskDetailData.members?.map(emp => ({ value: emp.employee_id, label: emp.name })) || [],
      });

    } catch (error) {
      console.error("Error fetching task details:", error);
      setIsError(true);
      setToastMessage("Failed to fetch task details");
      setIsToastOpen(true);
    }
  };

  const handleViewTask = async (taskId) => {
    try {
      setIsViewTaskModalOpen(true);
      const taskDetailData = await apiRequest(`/tasks/${taskId}`);
      setSelectedTask(taskDetailData);
    } catch (error) {
      console.error("Error fetching project details:", error);
      setIsError(true);
      setToastMessage("Failed to fetch project details");
      setIsToastOpen(true);
    }
  };

  const fetchProjects = async (employeeID) => {
    try {
      const projectData = await apiRequest(`/employees/${employeeID}/projects`);
      setProjects(projectData.projects);
      setTotalProjects(projectData.project_count);


    } catch (err) {
      console.error("Error fetching projects", err);
    }
  };

  const fetchEmployees = async () => {
    try {
      const employeeData = await apiRequest(`/employees`);
      const employees = employeeData.employees;
      const members = employees.filter(emp => emp.role === 'member');

      setEmployees(employeeData.employees);
      setMembers(members);

    } catch (err) {
      console.error("Error fetching projects", err);
    }
  };

  const fetchTasks = async (projectID) => {
    if(!projectID) return;
    try {
      const taskData = await apiRequest(`/projects/tasks/${projectID}`);
      setTasks(taskData.tasks);
      setTotalTasks(taskData.task_count)

    } catch (err) {
      console.error("Error fetching tasks ", err)
    }
  };


  useEffect(() => {
    const fetchAllData = async () => {
      try {
        await Promise.all([fetchProjects(userDetails.employee_id), fetchEmployees()]);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllData();
  }, []);

  useEffect(() => {
    if(projects[0] != null){
      fetchTasks(projects[0]?.project_id);
      setSelectedProject(projects[0])
    }
  }, [projects])

  useEffect(() => {
    if(selectedProject != null){
      fetchTasks(selectedProject.project_id);
    }
  }, [selectedProject])

  if (isLoading) {
    return <Loader />
  }


  return (
    <>

      <DialogComponent
        open={isAddTaskModalOpen}
        onOpenChange={closeAddTask}
        title="Add new task"
        description=""
        buttonText="Add Task"
        buttonColor="#E59178"
        onSubmit={() => handleCreateTask(selectedProject.project_id)}
      >

        <TaskForm
          members={members}
          formData={taskCreateData}
          onInputChange={handleTaskInput}
        />

      </DialogComponent>
      
      <DialogComponent
        open={isEditTaskModalOpen}
        onOpenChange={closeEditTask}
        loading={!selectedEditTask}
        title="Edit task"
        description=""
        buttonText="Save Changes"
        buttonColor="#E59178"
        onSubmit={handleEditTask}
      >
        <TaskForm
          members={members}
          formData={taskEditData}
          onInputChange={handleEditInput}
        />
    
      </DialogComponent>

      <DialogComponent
        open={isViewTaskModalOpen}
        loading={!selectedTask}
        onOpenChange={closeViewTask}
        title="Task Details"
        buttonText="Close"
        buttonColor="#E59178"
        onSubmit={closeViewTask}
      >
        {/* <ProjectDetails project={selectedProject} /> */}
        <TaskDetails task={selectedTask} />

      </DialogComponent>


      <ToastComponent
            open={isToastOpen}
            setOpen={setIsToastOpen}
            toastMessage={toastMessage}
            toastTitle={isError ? "Error Occurred ❌" : "All Set! ✅"}
      />

      <Navbar navTitle={`Welcome ${userDetails.name}!`}
        navDesc="Hello Manager"
        name={userDetails.name}
        email={userDetails.email_id}
        profileImage={userDetails.profile_image_url} />

      <div className={styles.PageContent}>
        <div className={styles.FirstColumn}>
          <div className={styles.KpisContainer}>


          <KpiCard title="Total Projects"
              Icon={VscFileSymlinkDirectory}
              color='#E59178'
              kpiValue={totalProjects}
              buttonTitle="Shaping Ideas"
            //   onClick={() => setIsAddProjectModalOpen(true)} 
            />


          <KpiCard title="Total Tasks"
              Icon={FaUsers}
              color="#82C468"
              kpiValue={totalTasks}
              buttonTitle="Add new task"
              onClick={() => { setIsAddTaskModalOpen(true) }}
            />
            
 
          
          </div>
          <div className={styles.TeamRow}>
            <ProjectCard  
                projects={projects}
                fetchProjects={fetchProjects}
                onViewClick={handleViewTasks}
                /> 
          </div>
        </div>

        <div className={styles.ProjectColumn}>
          <TaskCard 
            tasks={tasks}
            fetchTasks={fetchTasks}
            projectId = {selectedProject?.project_id}
            isEditing={isEditTaskModalOpen}
            onEditClick={openEditTask}
            onViewClick={handleViewTask} 
          />
        </div>
      </div>
    </>


  );
}

export default ManagerPage;
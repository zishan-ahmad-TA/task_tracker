import { useEffect, useState } from "react";
import ToastComponent from "../components/ui-elements/Toast";
import styles from './AdminPage.module.css';
import Navbar from '../components/shared/Navbar';
import KpiCard from "../components/shared/KpiCard";
import { FaUsers } from "react-icons/fa";
import { VscFileSymlinkDirectory } from "react-icons/vsc";
import ProjectCard from "../components/admin/ProjectCard";
import TeamCard from "../components/admin/TeamCard";
import DialogComponent from "../components/ui-elements/Dialog";
import apiRequest from "../utils/apiRequest";
import CreateProjectForm from "../components/admin/CreateProjectForm";
import EditProjectForm from "../components/admin/EditProjectForm";

const AdminPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [userDetails, setUserDetails] = useState(null);
  const [projects, setProjects] = useState([]);
  const [isAddProjectModalOpen, setIsAddProjectModalOpen] = useState(false);
  const [isEditProjectModalOpen, setIsEditProjectModalOpen] = useState(false);
  const [employee, setEmployees] = useState([]);
  const [managers, setManagers] = useState([]);
  const [members, setMembers] = useState([]);
  const [totalProjects, setTotalProjects] = useState('NA');
  const [totalEmployee, setTotalEmployee] = useState('NA');
  const [toastMessage, setToastMessage] = useState('');
  const [isToastOpen, setIsToastOpen] = useState(false);
  const [isError, setIsError] = useState(false);

  const [formData, setFormData] = useState({
    project_name: '',
    description: '',
    start_date: null,
    end_date: null,
    manager_ids: [],
    employee_ids: [],
  });

  const handleProjectInput = (key, value) => {
    setFormData(prevState => ({
      ...prevState,
      [key]: value,
    }));
  };

  const handleCreateProject = async () => {
    const payload = {
      ...formData,
      start_date: formData.start_date ? formData.start_date.toISOString() : null,
      end_date: formData.end_date ? formData.end_date.toISOString() : null,
      manager_ids: formData.manager_ids.map(manager => manager.value),
      employee_ids: formData.employee_ids.map(employee => employee.value),
    };

    try {
      await apiRequest('/projects', 'POST', payload);
      closeAddProject();
      setIsError(false);
      setToastMessage("Success! Your new project has been created!");
      setIsToastOpen(true);
      await fetchProjects();

    } catch (error) {
      setIsError(true);
      setToastMessage("Failed to create project");
      setIsToastOpen(true);
      console.error(error.message);
    }
  };

  const closeAddProject = () => {
    setIsAddProjectModalOpen(false);
  }

  const openEditProject = (projectId) => {
    setIsEditProjectModalOpen(true);
  }

  const closeEditProject = () => {
    setIsEditProjectModalOpen(false);
  }

  const fetchUserDetails = async () => {
    try {
      const userData = await apiRequest(`/get-userdetails`)
      setUserDetails(userData);
    } catch (err) {
      console.error("Error fetching user details:", err);
    }
  };

  const fetchProjects = async () => {
    try {
      const projectData = await apiRequest(`/projects`)
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
      const managers = employees.filter(emp => emp.role === 'manager');

      setEmployees(employeeData.employees);
      setMembers(members);
      setManagers(managers);
      setTotalEmployee(employeeData?.employee_count || 0);

    } catch (err) {
      console.error("Error fetching projects", err);
    }
  };

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        await Promise.all([fetchUserDetails(), fetchProjects(), fetchEmployees()]);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllData();
  }, []);


  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <DialogComponent
        open={isAddProjectModalOpen}
        onOpenChange={closeAddProject}
        title="Add new Project"
        description=""
        buttonText="Add Project"
        buttonColor="#E59178"
        onSubmit={handleCreateProject}
      >
        <CreateProjectForm
          members={members}
          managers={managers}
          formData={formData}
          onInputChange={handleProjectInput}
        />
      </DialogComponent>


      <DialogComponent
        open={isEditProjectModalOpen}
        onOpenChange={closeEditProject}
        title="Edit project"
        description=""
        buttonText="Save Changes"
        buttonColor="#E59178"
      // onSubmit={handleEditProject}
      >
        <EditProjectForm
          members={members}
          managers={managers}
          formData={formData}
        // onInputChange={handleEditInput}
        />
      </DialogComponent>

      <ToastComponent
        open={isToastOpen}
        setOpen={setIsToastOpen}
        toastMessage={toastMessage}
        toastTitle={isError ? "Error Occurred ❌" : "All Set! ✅"}
      />

      <Navbar navTitle={`Welcome ${userDetails.name}!`}
        navDesc="Ready to build the next big thing?"
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
              buttonTitle="Add new project"
              onClick={() => setIsAddProjectModalOpen(true)} />

            <KpiCard title="Team Size"
              Icon={FaUsers}
              color="#82C468"
              kpiValue={totalEmployee}
              buttonTitle="Manage team" />
          </div>
          <div className={styles.TeamRow}>
            <TeamCard employeeData={employee} />
          </div>
        </div>

        <div className={styles.ProjectColumn}>
          <ProjectCard projects={projects}
            fetchProjects={fetchProjects}
            isEditing={isEditProjectModalOpen}
            onEditClick={openEditProject} />
        </div>
      </div>
    </>


  );
};

export default AdminPage;

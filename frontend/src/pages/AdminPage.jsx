import { useEffect, useState } from "react";
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

const AdminPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [userDetails, setUserDetails] = useState(null);
  const [projects, setProjects] = useState([]);
  const [isAddProjectModalOpen, setIsProjectModalOpen] = useState(false);
  const [employee, setEmployees] = useState([]);
  const [managers, setManagers] = useState([]);
  const [members, setMembers] = useState([]);
  const [totalProjects, setTotalProjects] = useState(0);
  const [totalEmployee, setTotalEmployee] = useState([]);

  const closeAddProject = () => {
    setIsProjectModalOpen(false);
  }

  const onDeleteSuccess = () => {
    fetchProjects();
  }

  const fetchUserDetails = async () => {
    try {
      const userData = await apiRequest(`${import.meta.env.VITE_BACKEND_URL}/get-userdetails`)
      setUserDetails(userData);
    } catch (err) {
      console.error("Error fetching user details:", err);
    }
  };

  const fetchProjects = async () => {
    try {
      const projectData = await apiRequest(`${import.meta.env.VITE_BACKEND_URL}/projects`)
      setProjects(projectData.projects);
      setTotalProjects(projectData.project_count);

    } catch (err) {
      console.error("Error fetching projects", err);
    }
  };


  const fetchEmployees = async () => {
    try {
      const employeeData = await apiRequest(`${import.meta.env.VITE_BACKEND_URL}/employees`);
      const employees = employeeData.employees;
      const members = employees.filter(emp => emp.role === 'member');
      const managers = employees.filter(emp => emp.role === 'manager');

      setEmployees(employeeData.employees);
      setMembers(members);
      setManagers(managers);
      console.log(managers);
      setTotalEmployee(employeeData.employee_count);

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
      <DialogComponent open={isAddProjectModalOpen} onOpenChange={closeAddProject}
        title="Add new Project" description=""
        buttonText="Add Project" buttonColor="#E59178">
        <CreateProjectForm members={members} managers={managers}/>
      </DialogComponent>

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
              onClick={() => setIsProjectModalOpen(true)} />

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
          <ProjectCard projects={projects} onDeleteSuccess={onDeleteSuccess} members={members} managers={managers} />
        </div>
      </div>
    </>


  );
};

export default AdminPage;

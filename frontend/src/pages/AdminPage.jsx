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
  const [totalProjects, setTotalProjects] = useState('NA');
  const [totalEmployee, setTotalEmployee] = useState('NA');

  const [formData, setFormData] = useState({
    project_name: '',
    description: '',
    start_date: null,
    end_date: null,
    manager_ids: [],
    employee_ids: [],
  });

  const handleInputChange = (key, value) => {
    setFormData(prevState => ({
      ...prevState,
      [key]: value,
    }));
  };

  const handleFormSubmit = async () => {
    const payload = {
      ...formData,
      start_date: formData.start_date ? formData.start_date.toISOString() : null,
      end_date: formData.end_date ? formData.end_date.toISOString() : null,
      manager_ids: formData.manager_ids.map(manager => manager.value),
      employee_ids: formData.employee_ids.map(employee => employee.value),
    };

    try {
      await apiRequest('/projects', 'POST', payload);
      await fetchProjects();
      closeAddProject();
    } catch (error) {
      console.error('Failed to create project:', error.message);
    }
  };


  const closeAddProject = () => {
    setIsProjectModalOpen(false);
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
      console.log(employees)
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
        onSubmit={handleFormSubmit}
      >
        <CreateProjectForm
          members={members}
          managers={managers}
          formData={formData}
          onInputChange={handleInputChange}
        />
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
          <ProjectCard projects={projects} setProjects={setProjects} />
        </div>
      </div>
    </>


  );
};

export default AdminPage;

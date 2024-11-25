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
import Input from "../components/ui-elements/Input";

const AdminPage = () => {
  const [userDetails, setUserDetails] = useState(null);
  const [projects, setProjects] = useState([]);
  const [isAddProjectModalOpen, setIsProjectModalOpen] = useState(false);

  const [totalProjects, setTotalProjects] = useState(0);
  const [teamSize,] = useState(5);

  const closeAddProject = () => {
    setIsProjectModalOpen(false);
  }

  const onDeleteSuccess = () => {
    fetchProjects();
  }

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const userData = await apiRequest(`${import.meta.env.VITE_BACKEND_URL}/get-userdetails`)
        setUserDetails(userData);
      } catch (err) {
        console.error("Error fetching user details:", err);
      }
    };

    fetchUserDetails();
  }, []);

  const fetchProjects = async () => {
    try {
      const projectData = await apiRequest(`${import.meta.env.VITE_BACKEND_URL}/projects`)
      setProjects(projectData.projects);
      setTotalProjects(projectData.project_count);

    } catch (err) {
      console.error("Error fetching projects", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);



  if (!userDetails) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <DialogComponent open={isAddProjectModalOpen}
        onOpenChange={closeAddProject}
        title="Add new Project"
        description=""
        buttonText="Add Project"
        buttonColor="#E59178">
        <Input label="Project Name" />
        <Input label="Project Description" />

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
              kpiValue={teamSize}
              buttonTitle="Manage team" />
          </div>
          <div className={styles.TeamRow}>
            <TeamCard />
          </div>
        </div>

        <div className={styles.ProjectColumn}>
          <ProjectCard projects={projects} onDeleteSuccess={onDeleteSuccess} />
        </div>
      </div>
    </>


  );
};

export default AdminPage;

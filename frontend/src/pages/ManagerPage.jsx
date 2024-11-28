import { useEffect, useState } from "react";
import styles from './AdminPage.module.css';
import Navbar from '../components/shared/Navbar';
import KpiCard from "../components/shared/KpiCard";
import ProjectCard from "../components/admin/ProjectCard";
import TeamCard from "../components/admin/TeamCard";
import DialogComponent from "../components/ui-elements/Dialog";
import useApiRequest from "../hooks/apiRequest";
import ProjectForm from "../components/admin/ProjectForm";
import ProjectDetails from "../components/shared/ProjectDetails";

import { VscFileSymlinkDirectory } from "react-icons/vsc";


const ManagerPage = ({userDetails}) => {
    const apiRequest = useApiRequest();
    const [projects, setProjects] = useState([]);
    const [totalProjects, setTotalProjects] = useState('NA');


    const fetchProjects = async (employeeID) => {
        try {
          const projectData = await apiRequest(`/employees/${employeeID}/projects`)
          console.log(projectData)
          setProjects(projectData.projects);
          setTotalProjects(projectData.project_count);

    
        } catch (err) {
          console.error("Error fetching projects", err);
        }
    };

    useEffect(() => {
        const fetchAllData = async () => {
          try {
            await Promise.all([fetchProjects(userDetails.employee_id)]);
          } catch (error) {
            console.error("Error fetching data:", error);
          } finally {
            setIsLoading(false);
          }
        };
    
        fetchAllData();
    }, []);

    return (
        <>
          {/* <DialogComponent
            open={isAddProjectModalOpen}
            onOpenChange={closeAddProject}
            title="Add new Project"
            description=""
            buttonText="Add Project"
            buttonColor="#E59178"
            onSubmit={handleCreateProject}
          >
            <ProjectForm
              members={members}
              managers={managers}
              formData={projectCreateData}
              onInputChange={handleProjectInput}
            />
          </DialogComponent>
    
    
          <DialogComponent
            open={isEditProjectModalOpen}
            onOpenChange={closeEditProject}
            loading={!selectedEditProject}
            title="Edit project"
            description=""
            buttonText="Save Changes"
            buttonColor="#E59178"
            onSubmit={handleEditProject}
          >
            <ProjectForm
              members={members}
              managers={managers}
              formData={projectEditData}
              onInputChange={handleEditInput}
            />
    
          </DialogComponent>
    
    
          <DialogComponent
            open={isViewProjectModalOpen}
            loading={!selectedProject}
            onOpenChange={closeViewProject}
            title="Project Details"
            buttonText="Close"
            buttonColor="#E59178"
            onSubmit={closeViewProject}
          >
            <ProjectDetails project={selectedProject} />
          </DialogComponent>
    
    
          <DialogComponent
            open={changeRoleModalOpen}
            onOpenChange={closeChangeRole}
            title="Change Role"
            buttonText="Update Role"
            buttonColor="#E59178"
            onSubmit={handleChangeRole}
          >
            <ChangeRoles employees={employee}
              formData={changeRoleData} onInputChange={handleRoleInput} />
          </DialogComponent>
    
          <ToastComponent
            open={isToastOpen}
            setOpen={setIsToastOpen}
            toastMessage={toastMessage}
            toastTitle={isError ? "Error Occurred ❌" : "All Set! ✅"}
          /> */}
    
          <Navbar navTitle={`Welcome ${userDetails.name}!` }
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
                //   buttonTitle="Add new project"
                //   onClick={() => setIsAddProjectModalOpen(true)} 
                  />
    
                <KpiCard title="Total Tasks"
                //   Icon={FaUsers}
                   color="#82C468"
                //   kpiValue={totalEmployee}
                //   buttonTitle="Manage team"
                //   onClick={() => { setChangeRoleModalOpen(true) }}
                   />
              </div>
              <div className={styles.TeamRow}>
                {/* <TeamCard employeeData={employee} /> */}
              </div>
            </div>
    
            {/* <div className={styles.ProjectColumn}>
              <ProjectCard projects={projects}
                fetchProjects={fetchProjects}
                isEditing={isEditProjectModalOpen}
                onEditClick={openEditProject}
                onViewClick={handleViewProject} />
            </div> */}
          </div>
        </>
    
    
    );
}

export default ManagerPage;
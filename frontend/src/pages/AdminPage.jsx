import { useEffect, useState } from "react";
import styles from './AdminPage.module.css';
import Navbar from '../components/shared/Navbar';
import KpiCard from "../components/shared/KpiCard";
import { FaUsers } from "react-icons/fa";
import { VscFileSymlinkDirectory } from "react-icons/vsc";

const AdminPage = () => {
  const [userDetails, setUserDetails] = useState(null);

  const [totalProjects, ] = useState(100);
  const [teamSize, ] = useState(5);

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/get-userdetails`, {
          method: "GET",
          credentials: "include",
        });
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Failed to fetch user details.");
        }

        const data = await response.json();
        setUserDetails(data);
      } catch (err) {
        console.error("Error fetching user details:", err);
      }
    };

    fetchUserDetails();
  }, []);

  if (!userDetails) {
    return <div>Loading...</div>;
  }

  console.log(userDetails)

  return (

    <>
      <Navbar navTitle={`Welcome ${userDetails.name}!`}
        navDesc="Ready to build the next big thing?"
        name={userDetails.name}
        email={userDetails.email_id}
        profileImage={userDetails.profile_image_url} />
      <div className={styles.KpisContainer}>

        <KpiCard title="Total Projects" Icon={VscFileSymlinkDirectory} color='#E59178' kpiValue={totalProjects} buttonTitle="Add new project" />
        <KpiCard title="Team Size" Icon={FaUsers} color="#82C468" kpiValue={teamSize} buttonTitle="Manage team" />
      </div>

    </>


  );
};

export default AdminPage;

import { useEffect, useState } from "react";
import Navbar from '../components/shared/Navbar';

const AdminPage = () => {
  const [userDetails, setUserDetails] = useState(null);

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
    <Navbar navTitle="Dashboard"
      name={userDetails.name}
      email={userDetails.email_id}
      profileImage={userDetails.profile_image_url} />
  );
};

export default AdminPage;

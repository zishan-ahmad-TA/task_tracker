import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import useApiRequest from "./apiRequest";

const useAuth = () => {
    const [userDetails, setUserDetails] = useState(null);
    const [loading, setLoading] = useState(true); // Track loading
    const navigate = useNavigate();
    const location = useLocation();
    const apiRequest = useApiRequest();

    useEffect(() => {
        const fetchUserDetails = async () => {
            try {
                const userData = await apiRequest(`/get-userdetails`);
                if (userData) {
                    setUserDetails(userData);
                } else {
                    navigate("/login");
                }
            } catch (err) {
                console.error("Error fetching user details:", err);
                navigate("/login");
            } finally {
                setLoading(false);
            }
        };

        if (location.pathname !== "/login") {
            fetchUserDetails();
        } else {
            setLoading(false);
        }
    }, [location.pathname, navigate]);

    return { userDetails, loading };
};

export default useAuth;
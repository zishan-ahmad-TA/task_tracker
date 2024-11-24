export const getInitials = (name) => {
    if (!name) return "";
  
    const [firstName, lastName = ""] = name.trim().split(" ");
    return (firstName[0] + (lastName[0] || firstName[1] || "")).toUpperCase();
  };
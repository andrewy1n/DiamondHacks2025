import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import AppointmentCard from "./Components/AppointmentCard";
import AddButton from "./Components/AddButton";
import LoginButton from "./Components/Login";
import AppointmentTabs from "./Components/AppointmentTabs";
import RecordButton from "./Components/RecordButton";
// import LogoutButton from "./Components/Logout";
// import Profile from "./Components/Profile";
import { useAuth0 } from "@auth0/auth0-react";

function App() {
  const [appointments, setAppointments] = useState([
    {
      id: 1,
      title: "Appointment 1",
      name: "Patient Safety",
      date: "April 5th, 2025",
    },
    {
      id: 2,
      title: "Appointment 2",
      name: "Patient Safety",
      date: "April 10th, 2025",
    },
  ]);

  const handleAddAppointment = () => {
    const newId = appointments.length + 1;
    const newAppointment = {
      id: newId,
      title: `Appointment ${newId}`,
      name: "Patient Safety",
      date: "April 15th, 2025",
    };
    setAppointments([...appointments, newAppointment]);
  };
  return (
    <>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "20px",
          marginTop: "50px",
          flexWrap: "wrap",
        }}
      >
        {appointments.map((appt) => (
          <AppointmentCard
            key={appt.id}
            title={appt.title}
            name={appt.name}
            date={appt.date}
          />
        ))}
      </div>
      <LoginButton />
      {/* <LogoutButton />
      <Profile /> */}
      {/* Floating AddButton */}
      <div
        style={{
          position: "fixed",
          bottom: "70px",
          right: "70px",
          zIndex: 1000,
        }}
      >
        <AddButton onClick={handleAddAppointment} />
      </div>

      <AppointmentTabs />
      <div
        style={{
          position: "fixed",
          bottom: "70px",
          right: "360px",
          zIndex: 1000,
        }}
      >
        <RecordButton />
      </div>
    </>
  );
}

export default App;

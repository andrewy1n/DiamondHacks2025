import Image from "next/image";
import AppointmentCard from "./components/AppointmentCard"
// import AddButton from "./components/AddButton"
// import AppointmentTabs from "./components/AppointmentTabs"
import LoginButton from "./components/LoginButton"


export default function Home() {
  return (
    <> 
    <AppointmentCard/>

      {/* <AddButton /> */}
    <LoginButton/>


      {/* <AppointmentTabs /> */}
    
    </>
  );
}

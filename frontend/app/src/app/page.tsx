import Image from "next/image";
import AppointmentCard from "./components/AppointmentCard"
import AddButton from "./components/AddButton"
import AppointmentTabs from "./components/AppointmentTabs"


export default function Home() {
  return (
    <> 
    <AppointmentCard/>

      {/* <AddButton /> */}


      <AppointmentTabs />
    
    </>
  );
}

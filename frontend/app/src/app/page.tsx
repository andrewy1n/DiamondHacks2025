import Image from "next/image";
import AppointmentCard from "./components/AppointmentCard";
// import AddButton from "./components/AddButton"
// import AppointmentTabs from "./components/AppointmentTabs"
// import LoginButton from "./components/LoginButton";
// import LogoutButton from "./components/LogoutButton";
// import { auth0 } from "@/lib/auth0";

export default function Home() {
  // const session = await auth0.getSession();

  return (
    <>
      <div className="flex-col justify-between items-center mt-8">
        <h1 className="text-2xl font-bold text-center">Your Appointments</h1>
        <p className="text-gray-600 text-center mb-4">Welcome!</p>
        {/* <LoginButton /> */}
      </div>
      <AppointmentCard />
      {/* Other appointment-related components */}
    </>
    // <>
    //   {user ? (
    //     // User is logged in - show appointments and logout button
    //     <>
    //       <div className="flex justify-between items-center mb-6">
    //         <h1 className="text-2xl font-bold">Your Appointments</h1>
    //         <div className="flex gap-4">
    //           <p className="text-gray-600">Welcome, {user.name}!</p>
    //           <LogoutButton />
    //         </div>
    //       </div>
    //       <AppointmentCard />
    //       {/* Other appointment-related components */}
    //     </>
    //   ) : (
    //     // User is not logged in - show login button
    //     <div className="flex flex-col items-center justify-center min-h-[60vh]">
    //       <h1 className="text-2xl font-bold mb-4">
    //         Please log in to view your appointments
    //       </h1>
    //       <LoginButton />
    //     </div>
    //   )}
    // </>
  );
}

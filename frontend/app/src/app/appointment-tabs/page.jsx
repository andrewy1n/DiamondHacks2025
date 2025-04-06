"use client";
import { useState } from "react";
/*import { useRouter } from "next/Navigation";*/

export default function AppointmentTabs() {
  const [activeTab, setActiveTab] = useState("Notes");
  /*const router = useRouter();*/

  const tabClass = (tab) =>
    `px-4 py-2 rounded-t-lg font-medium cursor-pointer transition-all duration-200 ${
      activeTab === tab
        ? "bg-blue-500 text-white"
        : "bg-gray-200 text-gray-700 hover:bg-gray-300"
    }`;

  return (
    <div className="max-w-xl mx-auto mt-10">
      <h1 className="text-2xl font-semibold mb-4">Appointment Tabs</h1>

      <div className="flex space-x-2 border-b mb-6">
        <div
          onClick={() => setActiveTab("Notes")}
          className={tabClass("Notes")}
        >
          Notes
        </div>
        <div
          onClick={() => setActiveTab("Transcript")}
          className={tabClass("Transcript")}
        >
          Transcript
        </div>
      </div>

      <div className="p-4 bg-gray-100 rounded shadow">
        {activeTab === "Notes" && <p>This is the Notes content.</p>}
        {activeTab === "Transcript" && <p>This is the Transcript content.</p>}
      </div>

      <button
        /*onClick={() => router.push("/")} */
        className="px-4 by-2 bg-gray-700 text-white rounded hover:bg-grey-800 transition"
      >
        ← Back to Appointments
      </button>
    </div>
  );
}

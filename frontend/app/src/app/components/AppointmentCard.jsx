"use client";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import axios from "axios";
// import { getAccessToken } from "@auth0/nextjs-auth0";

function AppointmentCard() {
  const router = useRouter();
  // const { user, isLoading: isAuthLoading } = useUser();
  const [token, setToken] = useState(
    "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtJX3VfdkJ0RmdRZHNFdEhiSDFOZCJ9.eyJpc3MiOiJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMjgzNjk0NzY0NDMxNzUwMDA1NSIsImF1ZCI6WyJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9kZXYteDdqeDBiZDRrNXZuMmp1ci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzQzOTY3NTY0LCJleHAiOjE3NDM5NzQ3NjQsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXpwIjoiZ2VMSU5BZ3phRlVCV24xSmU2VDBMdkUzaDZNaXE0TTYifQ.ey3QsMPWiVHZaQWwTpdFYuhnJJXp473bssaVSVms_LAAijxCJGCQ36E9YcBQHMyusamV0gHSXQ7oowWsc7VgIJKbCnvnVI8NbvdFYDuv-F6BPjUjJMpXnILTEKh7uQohtjBVxkF8MaFO3Ehh-cafJg2CPzwZfDhqJ9JwV-8dZvLu_vC4yz12brtlTllMqqLdD_3LodoIOqF06SzBHFX7gXKPNi2WwyR5wXZwpkORjniY3Pc7Znd9f0_dQF-wXO_8WdT91Mf2UMgFTmVGaTFNPTGkvmwnd2IX1VCVwWf7hDBDUXFRs1dEKwpc1il8V-p4DGKFGqmPg0MjrR0uknUgvQ"
  );
  const [appointments, setAppointments] = useState([]);
  const [appointmentName, setAppointmentName] = useState("");
  const [appointmentDate, setAppointmentDate] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // useEffect(() => {
  //   const fetchToken = async () => {
  //     // if (!user) return;

  //     try {
  //       setLoading(true);
  //       const { accessToken } = await getAccessToken();

  //       if (!accessToken) {
  //         throw new Error("No access token available");
  //       }

  //       setToken(accessToken);
  //     } catch (err) {
  //       console.error("Token error:", err);
  //       setError("Failed to get authentication token");
  //     } finally {
  //       setLoading(false);
  //     }
  //   };

  //   fetchToken();
  // }, []);

  useEffect(() => {
    const fetchAppointments = async () => {
      if (!token) return;

      try {
        setLoading(true);
        const response = await axios.get(
          "https://9b19-128-54-18-77.ngrok-free.app/appointments",
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "ngrok-skip-browser-warning": "true",
            },
          }
        );
        console.log(
          "Appointments response data:",
          response.data,
          "Type:",
          typeof response.data
        );

        if (Array.isArray(response.data)) setAppointments(response.data);
      } catch (err) {
        setError(err.response?.data?.message || "Failed to fetch appointments");
        console.error("Error fetching appointments:", err);
        // Removed setAppointments([]) from here
      } finally {
        setLoading(false);
      }
    };

    fetchAppointments();
  }, []);

  useEffect(() => {
    console.log("Updated appointments state:", appointments);
  }, [appointments]);

  const handleSubmitForm = async (e) => {
    e.preventDefault();

    if (!appointmentName || !appointmentDate) {
      setError("Please fill in all fields");
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(
        "https://9b19-128-54-18-77.ngrok-free.app/appointments",
        {
          name: appointmentName,
          date: appointmentDate,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log(response.data);

      setAppointments((prev) => [...prev, response.data]);
      setAppointmentName("");
      setAppointmentDate("");
      setShowForm(false);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to create appointment");
      console.error("Error creating appointment:", err);
    } finally {
      setLoading(false);
    }
  };

  // if (isAuthLoading) {
  //   return <div className="text-center py-5">Loading authentication...</div>;
  // }

  // if (!user) {
  //   return (
  //     <div className="text-center py-5">Please log in to view appointments</div>
  //   );
  // }

  return (
    <div className="p-5 max-w-md mx-auto bg-[#D5C6B9] rounded-lg">
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      {!showForm ? (
        <div className="flex justify-center mb-5">
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-[#947D9E] text-white rounded hover:bg-[#5d4e63] transition"
            disabled={loading}
          >
            {loading ? "Loading..." : "+ Add Appointment"}
          </button>
        </div>
      ) : (
        <form
          onSubmit={handleSubmitForm}
          className="mb-5 p-5 rounded-lg bg-[#568A97]"
        >
          <h2 className="text-xl font-semibold mb-4">Create New Appointment</h2>

          <div className="mb-4">
            <label htmlFor="name" className="block mb-1 font-medium">
              Name:
            </label>
            <input
              id="name"
              type="text"
              value={appointmentName}
              onChange={(e) => setAppointmentName(e.target.value)}
              placeholder="Enter name"
              className="w-full p-2 rounded bg-[#F0E9D8]"
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <label htmlFor="date" className="block mb-1 font-medium">
              Date:
            </label>
            <input
              id="date"
              type="datetime-local"
              value={appointmentDate}
              onChange={(e) => setAppointmentDate(e.target.value)}
              className="w-full p-2 rounded bg-[#F0E9D8]"
              disabled={loading}
            />
          </div>

          <div className="flex justify-between">
            <button
              type="submit"
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save"}
            </button>

            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setError(null);
              }}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {loading && !showForm ? (
        <div className="text-center py-5">Loading appointments...</div>
      ) : (
        <div className="space-y-3">
          {/* {Array.isArray(appointments) ? (
            appointments.map((appointment) => (
              <div
                key={appointment._id} // Always use a unique identifier for keys
                onClick={() =>
                  router.push(`/appointment-tabs/${appointment._id}`)
                }
                className="p-3 border rounded-lg bg-white cursor-pointer hover:bg-grey-100 transition"
              >
                <p className="font-semibold">{appointment.name}</p>
                <p className="text-gray-600">
                  {new Date(appointment.date).toLocaleString()}
                </p>
              </div>
            ))
          ) : (
            <div className="p-3 text-center text-gray-500">
              {loading ? "Loading appointments..." : "No appointments found"}
            </div>
          )} */}

          {Array.isArray(appointments) &&
          appointments.every(
            (item) => typeof item === "object" && item !== null && "_id" in item
          ) ? (
            appointments.map((appointment, index) => (
              <div
                key={appointment._id || index} // fallback to index to avoid error
                onClick={() =>
                  router.push(`/appointment-tabs/${appointment._id || ""}`)
                }
                className="p-3 rounded-lg bg-[#568A97] cursor-pointer hover:bg-[#36565e] transition"
              >
                <p className="font-bold text-md text-[#F0E9D8]">
                  {appointment.name}
                </p>
                <p className="text-[#D5C6B9] text-xs">
                  {new Date(appointment.date).toLocaleString()}
                </p>
              </div>
            ))
          ) : (
            <div className="p-3 text-center text-gray-500">
              {loading ? "Loading appointments..." : "No appointments found"}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AppointmentCard;

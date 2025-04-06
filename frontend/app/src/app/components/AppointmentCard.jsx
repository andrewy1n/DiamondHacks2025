"use client";

import { useState, useEffect } from "react";

// ✅ Add your bearer token here
const BEARER_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6ImtJX3VfdkJ0RmdRZHNFdEhiSDFOZCJ9.eyJpc3MiOiJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDEwMjgzNjk0NzY0NDMxNzUwMDA1NSIsImF1ZCI6WyJodHRwczovL2Rldi14N2p4MGJkNGs1dm4yanVyLnVzLmF1dGgwLmNvbS9hcGkvdjIvIiwiaHR0cHM6Ly9kZXYteDdqeDBiZDRrNXZuMmp1ci51cy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNzQzOTIyNzgyLCJleHAiOjE3NDM5Mjk5ODIsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXpwIjoiZ2VMSU5BZ3phRlVCV24xSmU2VDBMdkUzaDZNaXE0TTYifQ.fIlXQiPwF_pdXRsu4nVcesywF16M99bYdstk3WY6dYLnNQ6_yviSzmsLEJs2LaStH_MJep6NmHxtWrniSACP66-4McM3sZa3nOTsEHqTagoJ9_IPrllj9fjNzEAMcmeOOCxizgImI30OHz0c7pgXKE0AgQYmwD7b4Pk78tK4KhASZVvvYiQ6bdcXVv2u9YAO2264dq6vV6SqQm9Eoso87jj_vI6WK2a7Zt-MHHoDuVlTVqB2sLbvZOgMi_VBvu9h4UYacn-fHHwHc5j59NAZBb5cqAouv9zb3wjiSeMlmiEEhR81ZLVQixVLu4Xs1l7iovXtsE6DLu1UHJ3sTBsxoQ";

function AppointmentCard() {
  const [appointments, setAppointments] = useState([]);

  const [appointmentName, setAppointmentName] = useState("");
  const [appointmentDate, setAppointmentDate] = useState("");
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/appointments", {
      headers: {
        "Authorization": `Bearer ${BEARER_TOKEN}`,
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Failed to fetch appointments");
        }
        return res.json();
      })
      .then((data) => {
        setAppointments(data);
      })
      .catch((err) => {
        console.error("Error fetching appointments:", err);
      });
  }, []);

  const handleShowForm = () => {
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setAppointmentName("");
    setAppointmentDate("");
  };

  const handleSubmitForm = async (e) => {
    e.preventDefault();

    if (!appointmentName || !appointmentDate) {
      return;
    }

    const newAppointment = {
      name: appointmentName,
      date: appointmentDate,
    };

    try {
      const response = await fetch("http://localhost:8000/appointments", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${BEARER_TOKEN}`,
        },
        body: JSON.stringify(newAppointment),
      });

      if (!response.ok) {
        throw new Error("Failed to create appointment");
      }

      const createdAppt = await response.json();
      setAppointments((prev) => [...prev, createdAppt]);

      setAppointmentName("");
      setAppointmentDate("");
      setShowForm(false);
    } catch (err) {
      console.error("Error creating appointment:", err);
    }
  };

  return (
    <div style={{ padding: "20px", maxWidth: "400px", margin: "0 auto", color: "black" }}>
      {!showForm && (
        <button
          onClick={handleShowForm}
          style={{
            padding: "10px 20px",
            backgroundColor: "#4CAF50",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            marginBottom: "20px",
          }}
        >
          + Add Appointment
        </button>
      )}

      {showForm && (
        <form
          onSubmit={handleSubmitForm}
          style={{
            border: "1px solid black",
            padding: "20px",
            borderRadius: "8px",
            marginBottom: "20px",
            backgroundColor: "#f9f9f9",
          }}
        >
          <h2>Create New Appointment</h2>

          <div style={{ marginBottom: "10px" }}>
            <label htmlFor="name">Name:</label>
            <input
              id="name"
              type="text"
              value={appointmentName}
              onChange={(e) => setAppointmentName(e.target.value)}
              placeholder="Enter name"
              style={{
                width: "100%",
                padding: "8px",
                marginTop: "4px",
                borderRadius: "4px",
                border: "1px solid #ccc",
              }}
            />
          </div>

          <div style={{ marginBottom: "10px" }}>
            <label htmlFor="date">Date:</label>
            <input
              id="date"
              type="date"
              value={appointmentDate}
              onChange={(e) => setAppointmentDate(e.target.value)}
              style={{
                width: "100%",
                padding: "8px",
                marginTop: "4px",
                borderRadius: "4px",
                border: "1px solid #ccc",
              }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <button
              type="submit"
              style={{
                padding: "8px 16px",
                backgroundColor: "#4CAF50",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Save
            </button>

            <button
              type="button"
              onClick={handleCancelForm}
              style={{
                padding: "8px 16px",
                backgroundColor: "#f44336",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      <div>
        {appointments.map((appointment) => (
          <div
            key={appointment._id || appointment.name}
            style={{
              border: "1px solid #ddd",
              borderRadius: "8px",
              padding: "10px",
              marginBottom: "10px",
              backgroundColor: "#fff",
            }}
          >
            <p style={{ margin: 0, fontWeight: "bold" }}>{appointment.name}</p>
            <p style={{ margin: 0, color: "#555" }}>{appointment.date}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AppointmentCard;

import { useState } from "react";

function AppointmentCard() {

  const [appointments, setAppointment] = useState([]);

  //inputs
  const [appointmentName, setAppointmentName]= useState([]);
  const [appointmentDate, setAppointmentDate]= useState([]);

  const [showForm, setShowForm] = useState(false);

  const handleShowForm = () => {
    setShowForm(true);
  }

  const handleCancelForm = () => {
    setShowForm(false);
    setAppointmentName("");
    setAppointmentDate("");
  }


  const handleSubmitForm = (e) => {
    e.preventDefault();

    if(!appointmentName || !appointmentDate) {
      return;
    }

    const newAppointment = {
      name: appointmentName,
      date: appointmentDate
    }

    setAppointment((prev) => [...prev, newAppointment]);

    setAppointmentName("");
    setAppointmentDate("");

    setShowForm(false);

  }


  
  return (

    <div>
      <button onClick={handleShowForm}>+ Add </button>

      {showForm && (
        <form
          onSubmit={handleSubmitForm}
          style={{
            border: "1px solid black"
          }}>

          <h1>Create New Appointment</h1>

          <div>
            <label htmlFor="name"> Name:</label>
            <input 
              id="name"
              type="text"
              value={appointmentName}
              onChange= {(e) => setAppointment(e.target.value)}
              placeholder="Enter nameee"
              />
          </div> 
          
          <div>
            <label htmlFor="date"> Date:</label>
            <input 
              id="date"
              type="date"
              value={appointmentDate}
              onChange= {(e) => setAppointment(e.target.value)}
              placeholder="Enter date"
              />
          </div> 
          
          <div>
            <button type="submit">Save Appointment</button>
            <button
              type = "button"
              onClick={handleCancelForm}
              style={}
            >

          </div> 

        </form>









      )}

      

      {/* <div>
        {appointments.map((appointment, index) => (

          <div>
            key = {index}
            style = {{
              border: "1px solid black"
            }}
     

          <p> {appointment.name} </p> 
          <p> {appointment.date} </p> 

          </div> 

        

        ))}

   
      </div> */}

    </div>

    // <div className="card" style={{ width: '18rem' }}>
    //   <div className="card-body">
    //     <h5 className="card-title">{title}</h5>
    //     <h6 className="card-subtitle mb-2 text-body-secondary">
    //       Name: {name}
    //     </h6>
    //     <h6 className="card-subtitle mb-2 text-body-secondary">
    //       Date: {date}
    //     </h6>
    //     <a href="#" className="btn btn-primary">
    //       Go somewhere
    //     </a>
    //   </div>
    // </div>  );
  );

};

export default AppointmentCard;

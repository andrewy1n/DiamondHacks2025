function AppointmentCard({title, name, date}) {
  return (
    <div className="card" style={{ width: '18rem' }}>
      <div className="card-body">
        <h5 className="card-title">{title}</h5>
        <h6 className="card-subtitle mb-2 text-body-secondary">
          Name: {name}
        </h6>
        <h6 className="card-subtitle mb-2 text-body-secondary">
          Date: {date}
        </h6>
        <a href="#" className="btn btn-primary">
          Go somewhere
        </a>
      </div>
    </div>
  );
}

export default AppointmentCard;

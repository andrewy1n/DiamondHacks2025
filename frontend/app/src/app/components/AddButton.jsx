function AddButton() {
    return (
      <button
        type="button"
        className="btn btn-secondary"
        data-bs-container="body"
        data-bs-toggle="popover"
        data-bs-placement="top"
        data-bs-content="Top popover"
      >
        +
      </button>
    );
  }
  
  export default AddButton;
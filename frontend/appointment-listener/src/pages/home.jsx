import React from "react";
import Profile from "../Components/Profile"
import ProtectedRoute from '../Components/ProtectedRoute';

function Home() {
    return (
        <ProtectedRoute>
            <h1>Hi!</h1>
            <Profile />
        </ProtectedRoute>
    );
}

export default Home;
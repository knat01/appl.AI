import React, { useState } from "react";
import axios from 'axios';

const TestConnection = () => {
    const [message, setMessage] = useState("");

    const testLambda = async () => {
        try {
            const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/test`);
            setMessage(response.data.message);
        } catch (error) {
            console.error('Error calling Lambda function:', error);
            setMessage('Error calling Lambda function');
        }
    };

    return (
        <div>
            <button onClick={testLambda}>Test Lambda Connection</button>
            <p>{message}</p>
        </div>
    );
};

export default TestConnection;

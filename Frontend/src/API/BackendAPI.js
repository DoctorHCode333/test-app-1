import axios from 'axios';
import BASE_URL from './BASE_URL';


export const authLogin = async (item) => {
    try {
        
        const response = await axios.post(`${BASE_URL}/api/login`, item);
        //console.log("ddrrpe",response);
        return response.data;

    } catch (error) {
        throw error;
    }
}

export const getAllConversationsFromDB = async (item) => {
    try {
        
        const response = await axios.post(`${BASE_URL}/api/getAllConversations`, item);
        //console.log("ddrrpe",response);
        return response.data;

    } catch (error) {
        throw error;
    }
}
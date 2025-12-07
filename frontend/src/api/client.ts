import axios from 'axios';
import type { FinalReview } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const client = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    reviewCode: async (code: string, language: string = 'python'): Promise<FinalReview> => {
        const response = await client.post<FinalReview>('/review/code', {
            code,
            language,
            filename: 'snippet',
        });
        return response.data;
    },

    reviewFile: async (filePath: string): Promise<FinalReview> => {
        const response = await client.post<FinalReview>('/review/file', {
            file_path: filePath,
        });
        return response.data;
    },

    getReviews: async (): Promise<any[]> => {
        const response = await client.get('/reviews');
        return response.data;
    }
};

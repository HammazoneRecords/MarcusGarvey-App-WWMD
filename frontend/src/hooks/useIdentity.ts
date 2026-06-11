import { useState, useEffect } from 'react';

const NAME_KEY = 'marcus_user_name';
const SESSION_KEY = 'marcus_session_id';

function generateSessionId(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = (Math.random() * 16) | 0;
        const v = c === 'x' ? r : (r & 0x3) | 0x8;
        return v.toString(16);
    });
}

export function useIdentity() {
    const [userName, setUserNameState] = useState<string>(() => localStorage.getItem(NAME_KEY) || '');
    const [sessionId] = useState<string>(() => {
        let id = localStorage.getItem(SESSION_KEY);
        if (!id) {
            id = generateSessionId();
            localStorage.setItem(SESSION_KEY, id);
        }
        return id;
    });

    const setUserName = (name: string) => {
        const trimmed = name.trim();
        localStorage.setItem(NAME_KEY, trimmed);
        setUserNameState(trimmed);
    };

    const needsName = !userName;

    return { userName, sessionId, setUserName, needsName };
}

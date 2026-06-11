import { useEffect, useRef, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Card } from '../components/ui/index';

export const AuthVerify = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { verifyMagicLink } = useAuth();
    const [error, setError] = useState<string | null>(null);
    const ranRef = useRef(false);

    useEffect(() => {
        if (ranRef.current) return;
        ranRef.current = true;

        const token = searchParams.get('token');
        if (!token) {
            setError('Missing sign-in token.');
            return;
        }

        verifyMagicLink(token).then(({ error }) => {
            if (error) {
                setError(error.message);
            } else {
                navigate('/profile', { replace: true });
            }
        });
    }, [searchParams, verifyMagicLink, navigate]);

    return (
        <div className="flex items-center justify-center min-h-[40vh]">
            <Card className="p-6 max-w-sm w-full text-center space-y-2">
                {error ? (
                    <>
                        <p className="text-sm font-bold text-red-600 dark:text-red-400">Sign-in failed</p>
                        <p className="text-xs text-zinc-500">{error}</p>
                    </>
                ) : (
                    <p className="text-sm text-zinc-500">Signing you in…</p>
                )}
            </Card>
        </div>
    );
};

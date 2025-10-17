import { useEffect } from "react";
import { useRouter } from "next/router";

export default function Home() {
    const router = useRouter();

    useEffect(() => {
        router.replace("/dashboard");
    }, [router]);

    // Show loading spinner while redirecting
    return (
        <div className="min-h-screen flex items-center justify-center bg-background">
            <div className="text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"></div>
                <p className="mt-4 text-muted-foreground">Redirecting...</p>
            </div>
        </div>
    );
}


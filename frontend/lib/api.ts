import { ChatMessage, DashboardStats, Period } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchDashboardStats(
    period: Period
): Promise<DashboardStats> {
    const response = await fetch(`${API_BASE_URL}/api/stats?period=${period}`);
    if (!response.ok) {
        throw new Error(`Failed to fetch stats: ${response.statusText}`);
    }
    return response.json();
}

/**
 * Chat API functions
 */

export async function getChatHistory(sessionId: string): Promise<ChatMessage[]> {
    const response = await fetch(
        `${API_BASE_URL}/api/chat/history?session_id=${sessionId}`
    );

    if (!response.ok) {
        throw new Error(`Failed to load chat history: ${response.statusText}`);
    }

    return response.json();
}

export async function sendChatMessage(
    sessionId: string,
    message: string,
    onToken: (token: string) => void,
    onComplete: () => void,
    onError: (error: string) => void
): Promise<void> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId, message }),
        });

        if (!response.ok) {
            onError(`Failed to send message: ${response.statusText}`);
            return;
        }

        // Parse SSE stream
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (!reader) {
            onError("Failed to get response stream");
            return;
        }

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text.split("\n");

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === "token") {
                            onToken(data.content);
                        } else if (data.type === "done") {
                            onComplete();
                            return;
                        } else if (data.type === "error") {
                            onError(data.content);
                            return;
                        }
                    } catch (e) {
                        // Skip malformed JSON
                        console.warn("Failed to parse SSE event:", line);
                    }
                }
            }
        }

        onComplete();
    } catch (error) {
        const errorMsg =
            error instanceof Error ? error.message : "Unknown error occurred";
        onError(errorMsg);
    }
}


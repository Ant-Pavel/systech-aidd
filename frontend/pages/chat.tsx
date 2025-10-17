import { FormEvent, useEffect, useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { ArrowLeft, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
    ChatBubble,
    ChatBubbleAvatar,
    ChatBubbleMessage,
} from "@/components/ui/chat-bubble";
import { ChatMessageList } from "@/components/ui/chat-message-list";
import { ChatInput } from "@/components/ui/chat-input";
import { getChatHistory, sendChatMessage } from "@/lib/api";
import { ChatMessage } from "@/types/api";

// Функция генерации/получения session ID
function getOrCreateSessionId(): string {
    if (typeof window === "undefined") return "";

    let sessionId = localStorage.getItem("chat_session_id");
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem("chat_session_id", sessionId);
    }
    return sessionId;
}

export default function Chat() {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [sessionId] = useState(() => getOrCreateSessionId());

    // Загрузка истории при монтировании
    useEffect(() => {
        const loadHistory = async () => {
            if (!sessionId) return;

            try {
                const history = await getChatHistory(sessionId);
                setMessages(history);
            } catch (err) {
                console.error("Failed to load chat history:", err);
                setError("Failed to load chat history");
            }
        };

        loadHistory();
    }, [sessionId]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMessage: ChatMessage = {
            role: "user",
            content: input,
            created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);
        setError(null);

        // Создаем временное сообщение для ассистента
        let assistantMessage: ChatMessage = {
            role: "assistant",
            content: "",
            created_at: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);

        await sendChatMessage(
            sessionId,
            userMessage.content,
            // onToken
            (token) => {
                assistantMessage = {
                    ...assistantMessage,
                    content: assistantMessage.content + token,
                };
                setMessages((prev) => {
                    const updated = [...prev];
                    updated[updated.length - 1] = assistantMessage;
                    return updated;
                });
            },
            // onComplete
            () => {
                setIsLoading(false);
            },
            // onError
            (errorMsg) => {
                setError(errorMsg);
                setIsLoading(false);
                // Удаляем последнее (неполное) сообщение ассистента
                setMessages((prev) => prev.slice(0, -1));
            }
        );
    };

    return (
        <>
            <Head>
                <title>AI Chat - Systech AIDD</title>
                <meta
                    name="description"
                    content="Chat with AI Assistant"
                />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <link rel="icon" href="/favicon.ico" />
            </Head>
            <div className="flex flex-col h-screen bg-background">
                {/* Header */}
                <header className="border-b p-4">
                    <div className="container mx-auto flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link href="/dashboard">
                                <Button variant="ghost" size="icon">
                                    <ArrowLeft className="h-5 w-5" />
                                </Button>
                            </Link>
                            <h1 className="text-2xl font-bold">AI Assistant</h1>
                        </div>
                    </div>
                </header>

                {/* Messages */}
                <main className="flex-1 overflow-hidden">
                    <ChatMessageList>
                        {messages.length === 0 && (
                            <div className="flex items-center justify-center h-full text-muted-foreground">
                                <p>Start a conversation with the AI assistant</p>
                            </div>
                        )}
                        {messages.map((message, index) => (
                            <ChatBubble
                                key={index}
                                variant={message.role === "user" ? "sent" : "received"}
                            >
                                <ChatBubbleAvatar
                                    className="h-8 w-8 shrink-0"
                                    fallback={message.role === "user" ? "U" : "AI"}
                                />
                                <ChatBubbleMessage
                                    variant={message.role === "user" ? "sent" : "received"}
                                    isLoading={message.role === "assistant" && message.content === "" && isLoading}
                                >
                                    {message.content}
                                </ChatBubbleMessage>
                            </ChatBubble>
                        ))}
                    </ChatMessageList>
                </main>

                {/* Input */}
                <footer className="border-t p-4">
                    <div className="container mx-auto">
                        {error && (
                            <div className="mb-4 rounded-lg border border-destructive bg-destructive/10 p-3">
                                <p className="text-sm text-destructive">{error}</p>
                            </div>
                        )}
                        <form
                            onSubmit={handleSubmit}
                            className="relative rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring p-1"
                        >
                            <ChatInput
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Type your message..."
                                className="min-h-12 resize-none rounded-lg bg-background border-0 p-3 shadow-none focus-visible:ring-0"
                                disabled={isLoading}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter" && !e.shiftKey) {
                                        e.preventDefault();
                                        handleSubmit(e);
                                    }
                                }}
                            />
                            <div className="flex items-center p-3 pt-0 justify-end">
                                <Button
                                    type="submit"
                                    size="sm"
                                    className="gap-1.5"
                                    disabled={isLoading || !input.trim()}
                                >
                                    Send
                                    <Send className="size-3.5" />
                                </Button>
                            </div>
                        </form>
                    </div>
                </footer>
            </div>
        </>
    );
}


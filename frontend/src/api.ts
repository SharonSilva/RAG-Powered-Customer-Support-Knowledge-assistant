const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export interface Source {
    ref: number;
    document_id: number;
    section_title: string | null;
    page_number: number | null;
}

export interface AskResponse{
    answer: string;
    sources: Source[];
    query_log_id: number;
}

export async function askQuestion(question: string, category?: string):
Promise<AskResponse>{
    const response = await fetch(`${API_BASE_URL}/ask`,{
        method: "POST",
        headers:{"Content-Type": "application/json"},
        body: JSON.stringify({question, category:category || null}),
    });

    if(!response.ok){
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
}

export async function submitFeedback(queryLogId: number, feedback: "up" | "down") : Promise<void>{
    const response = await fetch(`${API_BASE_URL}/query-logs/${queryLogId}/feedback`,{
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({feedback}),
    });

    if(!response.ok){
        throw new Error(`Feedback request failed: ${response.status}`);
    }
}

export interface UploadResponse{
    filename: string;
    document_id: number;
    category: string | null;
    num_chunks: number;
}

export async function uploadDocument(file: File, category?: string):
Promise<UploadResponse>{
    const formData = new FormData();
    formData.append("file", file);
    if(category){
        formData.append("category", category);
    }

    const response = await fetch(`${API_BASE_URL}/upload`, {
        method: "POST",
        body: formData,
    });

    if(!response.ok){
        throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
}


export interface AnalyticsSummary{
    overall: {
        total_queries: number;
        answered: number;
        fallback: number;
        fallback_rate_percent: number;
    };
    health_score: {
        knowledge_health_score: number;
        breakdown: Record<string, {value: number; weight: number; note?: string}>;
    };
}

export async function getAnalyticsSummary(): Promise<AnalyticsSummary> {
    const response = await fetch(`${API_BASE_URL}/analytics/summary`);

    if(!response.ok){
        throw new Error(`Analytics request failed: ${response.status}`);
    }

    return response.json();
}

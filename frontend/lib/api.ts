import type { Customer } from "./schema";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

const PREDICT_TIMEOUT_MS = 90_000;

export interface PredictResponse {
  churn_probability: number;
  will_churn: boolean;
  risk: "high" | "low";
  threshold: number;
  model_version: string;
}

async function postPredict(customer: Customer): Promise<PredictResponse> {
  const response = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customer),
    signal: AbortSignal.timeout(PREDICT_TIMEOUT_MS),
  });

  if (!response.ok) {
    throw new Error(`API ${response.status} xato qaytardi`);
  }

  return (await response.json()) as PredictResponse;
}

/**
 * Render free tier ~15 daqiqa harakatsizlikdan keyin uxlaydi -- birinchi so'rov
 * ~60 soniyagacha cho'zilishi mumkin. Shu sabab birinchi urinish timeout yoki
 * tarmoq xatosi bilan tugasa, bitta marta avtomatik qayta uriniladi.
 */
export async function predictChurn(
  customer: Customer,
  onRetry?: () => void
): Promise<PredictResponse> {
  try {
    return await postPredict(customer);
  } catch {
    onRetry?.();
    return await postPredict(customer);
  }
}

/** Sahifa ochilganda fonda chaqiriladi -- serverni "uyg'otish" uchun; natija va xato e'tiborsiz qoldiriladi. */
export async function warmUpServer(): Promise<void> {
  try {
    await fetch(`${API_URL}/health`, { signal: AbortSignal.timeout(PREDICT_TIMEOUT_MS) });
  } catch {
    // jim o'tkazib yuboriladi -- bu shunchaki "uyg'otish" urinishi
  }
}

const EXPLAIN_TIMEOUT_MS = 60_000;

export interface DriverImpact {
  feature: string;
  impact: number;
}

export interface ExplainResponse {
  explanation: string;
  source: "llm" | "template";
  top_drivers: DriverImpact[];
  churn_probability: number;
  risk: string;
}

/**
 * /predict'dan farqli o'laroq bu yerda avtomatik retry yo'q -- LLM chaqiruvi
 * sekinroq (backend'da 20 soniya timeout + 1 retry bor, shuning uchun frontend
 * timeout'i kattaroq). Xato bo'lsa, foydalanuvchi "Nega?" tugmasini qayta bosadi.
 */
export async function explainChurn(customer: Customer): Promise<ExplainResponse> {
  const response = await fetch(`${API_URL}/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(customer),
    signal: AbortSignal.timeout(EXPLAIN_TIMEOUT_MS),
  });

  if (!response.ok) {
    throw new Error(`API ${response.status} xato qaytardi`);
  }

  return (await response.json()) as ExplainResponse;
}

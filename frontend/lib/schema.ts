import { z } from "zod";

/**
 * api/schema.py dagi Customer bilan aynan bir xil 19 maydon, bir xil tartib va
 * bir xil tiplar (str -> string, int/float -> number). Har bir maydon uchun
 * ruxsat etilgan qiymatlar (dropdown options) app/page.tsx da alohida
 * saqlanadi -- backend ham faqat "str" qabul qiladi, qat'iy enum emas.
 */
export const customerSchema = z.object({
  gender: z.string().min(1),
  SeniorCitizen: z.number().int().min(0).max(1),
  Partner: z.string().min(1),
  Dependents: z.string().min(1),
  tenure: z.number().int().min(0),
  PhoneService: z.string().min(1),
  MultipleLines: z.string().min(1),
  InternetService: z.string().min(1),
  OnlineSecurity: z.string().min(1),
  OnlineBackup: z.string().min(1),
  DeviceProtection: z.string().min(1),
  TechSupport: z.string().min(1),
  StreamingTV: z.string().min(1),
  StreamingMovies: z.string().min(1),
  Contract: z.string().min(1),
  PaperlessBilling: z.string().min(1),
  PaymentMethod: z.string().min(1),
  MonthlyCharges: z.number().min(0),
  TotalCharges: z.number().min(0),
});

export type Customer = z.infer<typeof customerSchema>;

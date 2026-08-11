"use client";

import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { AlertTriangle, CheckCircle2, CreditCard, HelpCircle, Loader2, User, Wifi } from "lucide-react";
import { customerSchema, type Customer } from "@/lib/schema";
import {
  explainChurn,
  predictChurn,
  warmUpServer,
  type DriverImpact,
  type ExplainResponse,
  type PredictResponse,
} from "@/lib/api";

const YES_NO = ["Yes", "No"];

const defaultCustomer: Customer = {
  gender: "Female",
  SeniorCitizen: 0,
  Partner: "No",
  Dependents: "No",
  tenure: 12,
  PhoneService: "Yes",
  MultipleLines: "No",
  InternetService: "DSL",
  OnlineSecurity: "No",
  OnlineBackup: "No",
  DeviceProtection: "No",
  TechSupport: "No",
  StreamingTV: "No",
  StreamingMovies: "No",
  Contract: "Month-to-month",
  PaperlessBilling: "Yes",
  PaymentMethod: "Electronic check",
  MonthlyCharges: 70,
  TotalCharges: 840,
};

type Status = "idle" | "loading" | "retrying" | "error" | "success";
type ExplainStatus = "idle" | "loading" | "error" | "success";

export default function Home() {
  const [form, setForm] = useState<Customer>(defaultCustomer);
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [submittedCustomer, setSubmittedCustomer] = useState<Customer | null>(null);
  const [explainStatus, setExplainStatus] = useState<ExplainStatus>("idle");
  const [explainResult, setExplainResult] = useState<ExplainResponse | null>(null);
  const [explainError, setExplainError] = useState<string | null>(null);

  useEffect(() => {
    // Sahifa ochilganda fonda /health'ga so'rov yuboriladi -- Render serverini
    // "uyg'otish" uchun. Natija ekranga chiqarilmaydi, xato jim o'tkazib yuboriladi.
    void warmUpServer();
  }, []);

  function update<K extends keyof Customer>(key: K, value: Customer[K]) {
    setForm((prev) => {
      const next = { ...prev, [key]: value };
      if (key === "PhoneService" && value === "No") {
        next.MultipleLines = "No phone service";
      }
      if (key === "InternetService" && value === "No") {
        next.OnlineSecurity = "No internet service";
        next.OnlineBackup = "No internet service";
        next.DeviceProtection = "No internet service";
        next.TechSupport = "No internet service";
        next.StreamingTV = "No internet service";
        next.StreamingMovies = "No internet service";
      }
      return next;
    });
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const parsed = customerSchema.safeParse(form);
    if (!parsed.success) {
      setStatus("error");
      setErrorMessage(
        "Formada xato bor: " + parsed.error.issues.map((issue) => issue.message).join(", ")
      );
      return;
    }

    setStatus("loading");
    setErrorMessage(null);
    setResult(null);
    setSubmittedCustomer(null);
    setExplainStatus("idle");
    setExplainResult(null);
    setExplainError(null);

    try {
      const response = await predictChurn(parsed.data, () => setStatus("retrying"));
      setResult(response);
      setSubmittedCustomer(parsed.data);
      setStatus("success");
    } catch {
      setStatus("error");
      setErrorMessage(
        "API ishlamayapti yoki javob bermadi. Bir necha soniyadan so'ng qayta urinib ko'ring."
      );
    }
  }

  async function handleExplain() {
    if (!submittedCustomer) return;

    setExplainStatus("loading");
    setExplainError(null);

    try {
      const response = await explainChurn(submittedCustomer);
      setExplainResult(response);
      setExplainStatus("success");
    } catch {
      setExplainStatus("error");
      setExplainError("Tushuntirishni olishning iloji bo'lmadi, qayta urinib ko'ring");
    }
  }

  const noPhone = form.PhoneService === "No";
  const noInternet = form.InternetService === "No";
  const isBusy = status === "loading" || status === "retrying";

  return (
    <div className="min-h-screen bg-zinc-50 px-4 py-10 dark:bg-zinc-950 sm:py-16">
      <div className="mx-auto max-w-3xl">
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
            Telecom Churn Predictor
          </h1>
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
            Real-time churn bashorati — FastAPI backend orqali ishlaydi.
          </p>
        </header>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Section title="Profil" icon={<User className="h-5 w-5" />}>
            <SelectField
              label="Jinsi (gender)"
              value={form.gender}
              options={["Female", "Male"]}
              onChange={(v) => update("gender", v)}
            />
            <SelectField
              label="Keksa fuqaro (SeniorCitizen)"
              value={form.SeniorCitizen === 1 ? "Yes" : "No"}
              options={YES_NO}
              onChange={(v) => update("SeniorCitizen", v === "Yes" ? 1 : 0)}
            />
            <SelectField
              label="Turmush o'rtog'i bor (Partner)"
              value={form.Partner}
              options={YES_NO}
              onChange={(v) => update("Partner", v)}
            />
            <SelectField
              label="Qaramog'idagilar bor (Dependents)"
              value={form.Dependents}
              options={YES_NO}
              onChange={(v) => update("Dependents", v)}
            />
            <NumberField
              label="Mijozlik muddati, oy (tenure)"
              value={form.tenure}
              min={0}
              max={100}
              step={1}
              onChange={(v) => update("tenure", Math.round(v))}
            />
          </Section>

          <Section title="Xizmatlar" icon={<Wifi className="h-5 w-5" />}>
            <SelectField
              label="Telefon xizmati (PhoneService)"
              value={form.PhoneService}
              options={YES_NO}
              onChange={(v) => update("PhoneService", v)}
            />
            <SelectField
              label="Bir nechta liniya (MultipleLines)"
              value={form.MultipleLines}
              options={noPhone ? ["No phone service"] : YES_NO}
              onChange={(v) => update("MultipleLines", v)}
              disabled={noPhone}
            />
            <SelectField
              label="Internet xizmati (InternetService)"
              value={form.InternetService}
              options={["DSL", "Fiber optic", "No"]}
              onChange={(v) => update("InternetService", v)}
            />
            <SelectField
              label="Onlayn xavfsizlik (OnlineSecurity)"
              value={form.OnlineSecurity}
              options={noInternet ? ["No internet service"] : YES_NO}
              onChange={(v) => update("OnlineSecurity", v)}
              disabled={noInternet}
            />
            <SelectField
              label="Onlayn zaxira (OnlineBackup)"
              value={form.OnlineBackup}
              options={noInternet ? ["No internet service"] : YES_NO}
              onChange={(v) => update("OnlineBackup", v)}
              disabled={noInternet}
            />
            <SelectField
              label="Qurilma himoyasi (DeviceProtection)"
              value={form.DeviceProtection}
              options={noInternet ? ["No internet service"] : YES_NO}
              onChange={(v) => update("DeviceProtection", v)}
              disabled={noInternet}
            />
            <SelectField
              label="Texnik yordam (TechSupport)"
              value={form.TechSupport}
              options={noInternet ? ["No internet service"] : YES_NO}
              onChange={(v) => update("TechSupport", v)}
              disabled={noInternet}
            />
            <SelectField
              label="Streaming TV"
              value={form.StreamingTV}
              options={noInternet ? ["No internet service"] : YES_NO}
              onChange={(v) => update("StreamingTV", v)}
              disabled={noInternet}
            />
            <SelectField
              label="Streaming kino (StreamingMovies)"
              value={form.StreamingMovies}
              options={noInternet ? ["No internet service"] : YES_NO}
              onChange={(v) => update("StreamingMovies", v)}
              disabled={noInternet}
            />
          </Section>

          <Section title="Shartnoma va to'lov" icon={<CreditCard className="h-5 w-5" />}>
            <SelectField
              label="Shartnoma turi (Contract)"
              value={form.Contract}
              options={["Month-to-month", "One year", "Two year"]}
              onChange={(v) => update("Contract", v)}
            />
            <SelectField
              label="Qog'ozsiz billing (PaperlessBilling)"
              value={form.PaperlessBilling}
              options={YES_NO}
              onChange={(v) => update("PaperlessBilling", v)}
            />
            <SelectField
              label="To'lov usuli (PaymentMethod)"
              value={form.PaymentMethod}
              options={[
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
              ]}
              onChange={(v) => update("PaymentMethod", v)}
            />
            <NumberField
              label="Oylik to'lov, $ (MonthlyCharges)"
              value={form.MonthlyCharges}
              min={0}
              step={0.5}
              onChange={(v) => update("MonthlyCharges", v)}
            />
            <NumberField
              label="Jami to'lov, $ (TotalCharges)"
              value={form.TotalCharges}
              min={0}
              step={1}
              onChange={(v) => update("TotalCharges", v)}
            />
          </Section>

          <button
            type="submit"
            disabled={isBusy}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-zinc-900 px-6 py-3 font-medium text-white transition hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-60 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            {isBusy && <Loader2 className="h-5 w-5 animate-spin" />}
            {status === "loading" && "Server uyg'onmoqda (~50 soniya kutish mumkin)..."}
            {status === "retrying" && "Birinchi urinish muvaffaqiyatsiz — qayta urinilmoqda..."}
            {!isBusy && "Bashorat qilish"}
          </button>
        </form>

        {status === "error" && errorMessage && (
          <div className="mt-6 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {status === "success" && result && (
          <>
            <ResultCard result={result} />
            <ExplainSection
              status={explainStatus}
              result={explainResult}
              error={explainError}
              onExplain={handleExplain}
            />
          </>
        )}
      </div>
    </div>
  );
}

function Section({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-zinc-900 dark:text-zinc-50">
        {icon}
        {title}
      </h2>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">{children}</div>
    </div>
  );
}

function SelectField({
  label,
  value,
  options,
  onChange,
  disabled,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
  disabled?: boolean;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-zinc-700 dark:text-zinc-300">{label}</span>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 disabled:cursor-not-allowed disabled:bg-zinc-100 disabled:text-zinc-400 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50 dark:disabled:bg-zinc-900"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-zinc-700 dark:text-zinc-300">{label}</span>
      <input
        type="number"
        value={value}
        min={min}
        max={max}
        step={step}
        onChange={(event) => onChange(Number.isNaN(event.target.valueAsNumber) ? 0 : event.target.valueAsNumber)}
        className="rounded-lg border border-zinc-300 bg-white px-3 py-2 text-zinc-900 dark:border-zinc-700 dark:bg-zinc-800 dark:text-zinc-50"
      />
    </label>
  );
}

function ResultCard({ result }: { result: PredictResponse }) {
  const percent = Math.round(result.churn_probability * 1000) / 10;
  const isHigh = result.risk === "high";

  return (
    <div className="mt-6 rounded-xl border border-zinc-200 bg-white p-6 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">Churn ehtimoli</p>
          <p className="text-4xl font-bold text-zinc-900 dark:text-zinc-50">{percent}%</p>
        </div>
        <span
          className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium ${
            isHigh
              ? "bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300"
              : "bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300"
          }`}
        >
          {isHigh ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
          {isHigh ? "Yuqori risk" : "Past risk"}
        </span>
      </div>

      <div className="mt-4 h-3 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
        <div
          className={`h-full rounded-full transition-all ${isHigh ? "bg-red-500" : "bg-green-500"}`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

function ExplainSection({
  status,
  result,
  error,
  onExplain,
}: {
  status: ExplainStatus;
  result: ExplainResponse | null;
  error: string | null;
  onExplain: () => void;
}) {
  const isLoading = status === "loading";

  return (
    <div className="mt-6">
      <button
        type="button"
        onClick={onExplain}
        disabled={isLoading}
        className="flex items-center gap-2 rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-700 transition hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-200 dark:hover:bg-zinc-800"
      >
        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <HelpCircle className="h-4 w-4" />}
        {isLoading ? "Tahlil qilinmoqda..." : "Nega?"}
      </button>

      {status === "error" && error && (
        <p className="mt-2 flex items-center gap-1.5 text-sm text-red-600 dark:text-red-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {error}
        </p>
      )}

      {status === "success" && result && (
        <div className="mt-3 rounded-xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">
            {result.explanation}
          </p>

          {result.top_drivers.length > 0 && (
            <div className="mt-4">
              <h3 className="mb-2 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                Asosiy omillar
              </h3>
              <DriverList drivers={result.top_drivers.slice(0, 5)} />
            </div>
          )}

          {result.source === "template" && (
            <p className="mt-3 text-xs text-zinc-400 dark:text-zinc-500">
              Shablon javob (AI mavjud emas)
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function DriverList({ drivers }: { drivers: DriverImpact[] }) {
  const maxImpact = Math.max(...drivers.map((driver) => Math.abs(driver.impact)), 0.0001);

  return (
    <ul className="space-y-2">
      {drivers.map((driver) => {
        const widthPercent = Math.round((Math.abs(driver.impact) / maxImpact) * 100);
        return (
          <li key={driver.feature}>
            <div className="mb-1 flex items-center justify-between gap-2 text-sm">
              <span className="text-zinc-700 dark:text-zinc-300">{driver.feature}</span>
              <span className="text-zinc-500 dark:text-zinc-400">{driver.impact.toFixed(3)}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div
                className="h-full rounded-full bg-zinc-500 dark:bg-zinc-400"
                style={{ width: `${widthPercent}%` }}
              />
            </div>
          </li>
        );
      })}
    </ul>
  );
}

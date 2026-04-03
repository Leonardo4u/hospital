import type { SinaisVitaisInput } from "@/shared/types";

interface SinaisVitaisFormProps {
  valores: Partial<SinaisVitaisInput>;
  erros: Record<string, string>;
  alertas: { campo: string; alerta: "critico" | "atencao" }[];
  onChange: (campo: keyof SinaisVitaisInput, valor: number | undefined) => void;
}

interface CampoSinalVital {
  campo: keyof SinaisVitaisInput;
  label: string;
  unidade: string;
  min: number;
  max: number;
  step?: number;
}

const CAMPOS: CampoSinalVital[] = [
  { campo: "frequencia_cardiaca", label: "Frequencia cardiaca", unidade: "bpm", min: 20, max: 300 },
  { campo: "pressao_sistolica", label: "Pressao sistolica", unidade: "mmHg", min: 40, max: 300 },
  { campo: "pressao_diastolica", label: "Pressao diastolica", unidade: "mmHg", min: 20, max: 200 },
  { campo: "saturacao_o2", label: "Saturacao O2", unidade: "%", min: 50, max: 100, step: 0.1 },
  { campo: "temperatura", label: "Temperatura", unidade: "°C", min: 28, max: 45, step: 0.1 },
  { campo: "frequencia_respiratoria", label: "Frequencia respiratoria", unidade: "irpm", min: 4, max: 60 },
  { campo: "glasgow", label: "Escala de Glasgow", unidade: "pontos", min: 3, max: 15 },
];

export function SinaisVitaisForm({
  valores,
  erros,
  alertas,
  onChange,
}: SinaisVitaisFormProps) {
  return (
    <section className="space-y-5">
      <div>
        <h2 className="font-serif text-2xl text-slate-900">Sinais vitais</h2>
        <p className="text-sm text-slate-500">
          Preencha os sinais atuais para orientar a classificacao clinica.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        {CAMPOS.map((item) => {
          const erro = erros[item.campo];
          const alerta = alertas.find((entrada) => entrada.campo === item.campo);
          const valorAtual = valores[item.campo];

          const classeVisual = erro
            ? "border-red-400 bg-red-50"
            : alerta?.alerta === "critico"
              ? "border-orange-400 bg-orange-50"
              : alerta?.alerta === "atencao"
                ? "border-amber-300 bg-amber-50"
                : "border-slate-200 bg-white";

          return (
            <div key={item.campo} className={`rounded-3xl border p-4 ${classeVisual}`}>
              <div className="mb-3 flex items-start justify-between gap-3">
                <div>
                  <label
                    className="text-sm font-medium text-slate-700"
                    htmlFor={item.campo}
                  >
                    {item.label}
                  </label>
                  <p className="text-xs text-slate-500">{item.unidade}</p>
                </div>

                {erro ? (
                  <span className="text-lg leading-none text-red-600">⚠</span>
                ) : alerta?.alerta === "critico" ? (
                  <span className="rounded-full bg-orange-600 px-2 py-1 text-xs font-semibold text-white">
                    Critico
                  </span>
                ) : alerta?.alerta === "atencao" ? (
                  <span className="rounded-full bg-amber-400 px-2 py-1 text-xs font-semibold text-slate-900">
                    Atencao
                  </span>
                ) : null}
              </div>

              <input
                id={item.campo}
                type="number"
                min={item.min}
                max={item.max}
                step={item.step ?? 1}
                value={valorAtual ?? ""}
                onChange={(event) => {
                  const bruto = event.target.value;
                  if (bruto.trim() === "") {
                    onChange(item.campo, undefined);
                    return;
                  }
                  onChange(item.campo, Number(bruto));
                }}
                className="w-full rounded-2xl border border-slate-300 px-4 py-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              {erro ? <p className="mt-2 text-sm text-red-600">{erro}</p> : null}
            </div>
          );
        })}
      </div>
    </section>
  );
}
